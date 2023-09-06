from channels.testing import WebsocketCommunicator
from django.test import TestCase
from chat.consumers import ChatConsumer

class ConsumerTestCase(TestCase):

    async def test_consumer(self):
        # Instantiate the communicator
        communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")

        # Connect to the WebSocket
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Receive and assert the initial connection message
        response = await communicator.receive_json_from()
        self.assertEqual(response, {
            "type": "connection_established",
            "message": "You are now connected!"
        })

        # Test sending and receiving a message
        await communicator.send_json_to({
            "type": "share.post",
            "post_id": "1",
            "shared_by_username": "test_user",
        })

        # Receive and assert the shared post message
        response = await communicator.receive_json_from()
        self.assertEqual(response, {
            "message": "User test_user has shared a post with you. Click here to view the post: 1"
        })

        # Close the connection
        await communicator.disconnect()