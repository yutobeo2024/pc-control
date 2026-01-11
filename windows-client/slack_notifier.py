"""
Slack Notifier - Gửi thông báo đến Slack khi có yêu cầu mở máy
"""

import requests
import json


class SlackNotifier:
    def __init__(self, webhook_url=None):
        """
        Khởi tạo Slack Notifier
        webhook_url: URL của Slack Incoming Webhook
        """
        self.webhook_url = webhook_url or self._load_webhook_url()

    def _load_webhook_url(self):
        """Load webhook URL từ file config"""
        try:
            with open('slack_webhook.txt', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def send_unlock_request(self, device_name, device_id, web_app_url):
        """
        Gửi thông báo yêu cầu mở máy
        """
        if not self.webhook_url:
            print("Slack webhook not configured")
            return False

        # Tạo message với button
        message = {
            "text": f"🔔 *Yêu cầu mở máy* - {device_name}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔔 Yêu cầu mở máy",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Thiết bị:*\n{device_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Device ID:*\n`{device_id[:8]}...`"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Nhấn nút bên dưới để duyệt yêu cầu:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "✅ Mở Web App & Duyệt",
                                "emoji": True
                            },
                            "style": "primary",
                            "url": web_app_url
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 200:
                print(f"Slack notification sent successfully")
                return True
            else:
                print(f"Failed to send Slack notification: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False

    def send_time_warning(self, device_name, minutes_remaining):
        """
        Gửi cảnh báo khi sắp hết thời gian
        """
        if not self.webhook_url:
            return False

        message = {
            "text": f"⚠️ {device_name} - Còn {minutes_remaining} phút",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ *{device_name}*\nCòn *{minutes_remaining} phút* sẽ hết giờ"
                    }
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending warning: {e}")
            return False

    def send_time_expired(self, device_name):
        """
        Gửi thông báo khi hết giờ
        """
        if not self.webhook_url:
            return False

        message = {
            "text": f"🔒 {device_name} - Đã hết giờ và bị khóa",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔒 *{device_name}*\nĐã hết giờ và bị khóa tự động"
                    }
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending expired notification: {e}")
            return False

    def send_emergency_unlock(self, device_name):
        """
        Gửi thông báo khi emergency unlock được kích hoạt
        """
        if not self.webhook_url:
            return False

        message = {
            "text": f"🆘 {device_name} - EMERGENCY UNLOCK!",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🆘 EMERGENCY UNLOCK",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{device_name}*\nMáy đã được mở khóa khẩn cấp bởi admin!\n_(Server/webapp có thể đang gặp sự cố)_"
                    }
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message),
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending emergency unlock notification: {e}")
            return False


def configure_slack_webhook():
    """
    Helper function để cấu hình webhook URL
    """
    print("\n=== Slack Webhook Configuration ===")
    print("Để nhận thông báo qua Slack:")
    print("1. Tạo Incoming Webhook tại: https://api.slack.com/messaging/webhooks")
    print("2. Copy Webhook URL")
    print("3. Paste vào đây\n")

    webhook_url = input("Nhập Slack Webhook URL (hoặc Enter để bỏ qua): ").strip()

    if webhook_url:
        if webhook_url.startswith('https://hooks.slack.com/'):
            with open('slack_webhook.txt', 'w') as f:
                f.write(webhook_url)
            print("✅ Đã lưu webhook URL!")
            return webhook_url
        else:
            print("❌ URL không hợp lệ")
            return None
    return None


if __name__ == "__main__":
    # Test configuration
    configure_slack_webhook()
