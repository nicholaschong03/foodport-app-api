import json
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "You are now connected!"
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")

        if message_type == "share.post":
            self.share_post(text_data_json)
        else:
            message = text_data_json.get("message")
            if message:
                self.send(text_data=json.dumps({
                    'message': message
                }))

    def share_post(self, event):
        # This method handles the message type "share.post" and sends a notification to the user
        post_id = event["post_id"]
        shared_by_username = event["shared_by_username"]

        # Create a message to notify the user about the shared post
        message = f"User {shared_by_username} has shared a post with you. Click here to view the post: {post_id}"

        # Send the message to the WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))