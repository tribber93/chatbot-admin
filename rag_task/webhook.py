import io
import json
import os

import requests
from dotenv import load_dotenv
import regex as re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rag_task.inference_function import generate_chat
from django.db.models import F

# Access token for your WhatsApp business account app
whatsapp_token = os.getenv("WHATSAPP_TOKEN")

# Verify Token defined when configuring the webhook
verify_token = os.getenv("VERIFY_TOKEN")

# Message log dictionary to enable conversation over multiple messages
message_log_dict = {}

# send the response as a WhatsApp message back to the user
def send_whatsapp_message(body, message):
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    url = "https://graph.facebook.com/v16.0/" + phone_number_id + "/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=data, headers=headers)
    # print(f"whatsapp message response: {response.json()}")
    response.raise_for_status()


# create a message log for each phone number and return the current message log
def update_message_log(message, phone_number, role):
    initial_log = {
        "role": "system",
        "content": "You are a helpful assistant named WhatsBot.",
    }
    if phone_number not in message_log_dict:
        message_log_dict[phone_number] = [initial_log]
    message_log = {"role": role, "content": message}
    message_log_dict[phone_number].append(message_log)
    return message_log_dict[phone_number]


# remove last message from log if RAG request fails
def remove_last_message_from_log(phone_number):
    message_log_dict[phone_number].pop()


# make request to RAG
def make_rag_request(message, from_number):
    try:        
        result = generate_chat(message, clean_response=True)        
        response_message = result["answer"]
        
        print(f"RAG response: {response_message}")
        update_message_log(response_message, from_number, "assistant")
    except Exception as e:
        print(f"RAG error: {e}")
        response_message = "Sorry, the RAG API is currently overloaded or offline. Please try again later."
        remove_last_message_from_log(from_number)
    return response_message


# handle WhatsApp messages of different type
def handle_whatsapp_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
    response = make_rag_request(message_body, message["from"])
    send_whatsapp_message(body, response)


# handle incoming webhook messages
def handle_message(request):
    # Parse Request body in json format
    body = json.loads(request.body.decode('utf-8'))
    # print(f"request body: {body}")

    try:
        # info on WhatsApp text message payload:
        # https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples#text-messages
        if body.get("object"):
            if (
                body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
                and body["entry"][0]["changes"][0]["value"]["messages"][0]
            ):
                handle_whatsapp_message(body)
            return JsonResponse({"status": "ok"}, status=200)
        else:
            # if the request is not a WhatsApp API event, return an error
            return (
                JsonResponse({"status": "error", "message": "Not a WhatsApp API event"}, status=404)
            )
    # catch all other errors and return an internal server error
    except Exception as e:
        print(f"unknown error: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# Required webhook verifictaion for WhatsApp
# info on verification request payload:
# https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests
def verify(request):
    # Parse params from the webhook verification request
    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == verify_token:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return HttpResponse(challenge, status=200)
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            return JsonResponse({"status": "error", "message": "Verification failed"}, status=403)
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        return JsonResponse({"status": "error", "message": "Missing parameters"}, status=400)


# Sets homepage endpoint and welcome message
def home(request):
    return JsonResponse({"response":"WhatsApp RAG Webhook is listening!"})


# Accepts POST and GET requests at /webhook endpoint
@csrf_exempt
def webhook(request):
    if request.method == "GET":
        return verify(request)
    elif request.method == "POST":
        return handle_message(request)


# Route to reset message log
def reset(request):
    global message_log_dict
    message_log_dict = {}
    return JsonResponse({"response":"Message log resetted!"})

