
import os
import requests
import json
from datetime import datetime
import traceback

# Discord Webhook URLs
DISCORD_WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SYNC_URL = os.getenv("WEBHOOK_SYNC_URL", "https://discord.com/api/webhooks/1440954417330524171/loj9k4Bcmla30-zgNncoilau6NNHpPgyL_KXAgPSyHiRYq4qse8rZeTfDBpHz0S_Ohig")


def send_discord_embed(title, description, color, fields=None, footer=None, thumbnail=None, webhook_url=None):
    """
    Gửi embed message đến Discord webhook
    
    Args:
        title: Tiêu đề embed
        description: Mô tả chính
        color: Màu embed (decimal) - 0x00ff00 = green, 0xff0000 = red, 0xffaa00 = orange
        fields: List của dict với 'name', 'value', 'inline' (optional)
        footer: Text footer
        thumbnail: URL ảnh thumbnail
        webhook_url: Custom webhook URL (default: DISCORD_WEBHOOK_URL)
    """
    try:
        # Use custom webhook URL or default
        target_webhook = webhook_url or DISCORD_WEBHOOK_URL
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": fields or []
        }
        
        if footer:
            embed["footer"] = {"text": footer}
        
        if thumbnail:
            embed["thumbnail"] = {"url": thumbnail}
        
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(
            target_webhook,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print(f"[DISCORD WEBHOOK] ✅ Sent: {title}")
            return True
        else:
            print(f"[DISCORD WEBHOOK] ❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[DISCORD WEBHOOK] ❌ Exception: {e}")
        traceback.print_exc()
        return False


def log_order_created(uid, timestamp=None):
    """Log khi đơn hàng mới được tạo"""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return send_discord_embed(
        title="<:tick:1441683459012821002> Đơn Hàng Mới",
        description=f"Đơn hàng mới đã được tạo trong hệ thống",
        color=0x3498db,  # Blue
        fields=[
            {"name": "UID", "value": f"`{uid}`", "inline": True},
            {"name": "Trạng thái", "value": "Chờ thanh toán", "inline": True},
            {"name": "Thời gian", "value": timestamp, "inline": False}
        ],
        footer="VIP Key System - Order Tracking"
    )


def log_payment_confirmed(uid, amount, period, promo_code=None, tx_details=None):
    """Log khi thanh toán được xác nhận"""
    period_names = {"1d": "1 ngày", "7d": "7 ngày", "30d": "30 ngày", "90d": "90 ngày"}
    period_display = period_names.get(period, period)
    
    fields = [
        {"name": "UID", "value": f"`{uid}`", "inline": True},
        {"name": "Số tiền", "value": f"{amount:,} VNĐ", "inline": True},
        {"name": "Gói", "value": period_display, "inline": True}
    ]
    
    if promo_code:
        fields.append({"name": "Mã giảm giá", "value": f"`{promo_code}`", "inline": True})
    
    if tx_details:
        fields.append({"name": "Chi tiết giao dịch", "value": f"```{tx_details[:200]}```", "inline": False})
    
    return send_discord_embed(
        title="<:CarteTired:1442053976710185155> Thanh Toán Thành Công",
        description=f"Thanh toán đã được xác nhận qua MBBank API",
        color=0x2ecc71,  # Green
        fields=fields,
        footer="VIP Key System - Payment Confirmed"
    )


def log_key_sent(uid, email, key, period, success=True, error_msg=None):
    """Log khi key được gửi qua email"""
    period_names = {"1d": "1 ngày", "7d": "7 ngày", "30d": "30 ngày", "90d": "90 ngày"}
    period_display = period_names.get(period, period)
    
    if success:
        fields = [
            {"name": "UID", "value": f"`{uid}`", "inline": True},
            {"name": "Email", "value": email, "inline": True},
            {"name": "Gói", "value": period_display, "inline": True},
            {"name": "Key", "value": f"||`{key}`||", "inline": False}
        ]
        
        return send_discord_embed(
            title="✅ Key Đã Gửi",
            description=f"Key đã được gửi thành công qua email",
            color=0x27ae60,  # Dark green
            fields=fields,
            footer="VIP Key System - Key Delivery"
        )
    else:
        fields = [
            {"name": "UID", "value": f"`{uid}`", "inline": True},
            {"name": "Email", "value": email, "inline": True},
            {"name": "Lỗi", "value": f"```{error_msg[:200]}```", "inline": False}
        ]
        
        return send_discord_embed(
            title="❌ Gửi Key Thất Bại",
            description=f"Không thể gửi key qua email",
            color=0xe74c3c,  # Red
            fields=fields,
            footer="VIP Key System - Key Delivery Failed"
        )


def log_api_error(api_name, error_msg, details=None):
    """Log lỗi API"""
    fields = [
        {"name": "API", "value": api_name, "inline": True},
        {"name": "Thời gian", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True},
        {"name": "Lỗi", "value": f"```{error_msg[:500]}```", "inline": False}
    ]
    
    if details:
        fields.append({"name": "Chi tiết", "value": f"```{str(details)[:500]}```", "inline": False})
    
    return send_discord_embed(
        title="⚠️ Lỗi API",
        description=f"Phát hiện lỗi khi gọi API",
        color=0xe67e22,  # Orange
        fields=fields,
        footer="VIP Key System - API Error"
    )


def log_github_sync(action, file_path, success=True, error_msg=None):
    """Log GitHub sync operations"""
    if success:
        return send_discord_embed(
            title="🔄 GitHub Sync",
            description=f"Đồng bộ dữ liệu với GitHub thành công",
            color=0x9b59b6,  # Purple
            fields=[
                {"name": "Hành động", "value": action, "inline": True},
                {"name": "File", "value": f"`{file_path}`", "inline": True},
                {"name": "Trạng thái", "value": "✅ Thành công", "inline": False}
            ],
            footer="VIP Key System - GitHub Integration"
        )
    else:
        return send_discord_embed(
            title="⚠️ GitHub Sync Error",
            description=f"Lỗi khi đồng bộ với GitHub",
            color=0xe74c3c,  # Red
            fields=[
                {"name": "Hành động", "value": action, "inline": True},
                {"name": "File", "value": f"`{file_path}`", "inline": True},
                {"name": "Lỗi", "value": f"```{error_msg[:300]}```", "inline": False}
            ],
            footer="VIP Key System - GitHub Integration"
        )


def log_flyio_deployment(status, version=None, logs=None):
    """Log Fly.io deployment events"""
    if status == "success":
        fields = [
            {"name": "Trạng thái", "value": "✅ Deploy thành công", "inline": True},
            {"name": "Thời gian", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
        ]
        
        if version:
            fields.append({"name": "Version", "value": f"`{version}`", "inline": False})
        
        return send_discord_embed(
            title="🚀 Fly.io Deployment",
            description="Application đã được deploy thành công",
            color=0x3498db,  # Blue
            fields=fields,
            footer="VIP Key System - Fly.io"
        )
    else:
        fields = [
            {"name": "Trạng thái", "value": "❌ Deploy thất bại", "inline": True},
            {"name": "Thời gian", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
        ]
        
        if logs:
            fields.append({"name": "Logs", "value": f"```{logs[:500]}```", "inline": False})
        
        return send_discord_embed(
            title="⚠️ Fly.io Deployment Failed",
            description="Deployment gặp lỗi",
            color=0xe74c3c,  # Red
            fields=fields,
            footer="VIP Key System - Fly.io"
        )


def log_system_status(status, metrics=None):
    """Log system health status"""
    if status == "healthy":
        color = 0x2ecc71  # Green
        title = "✅ System Healthy"
        description = "Hệ thống hoạt động bình thường"
    elif status == "warning":
        color = 0xf39c12  # Yellow
        title = "⚠️ System Warning"
        description = "Hệ thống có cảnh báo"
    else:
        color = 0xe74c3c  # Red
        title = "❌ System Critical"
        description = "Hệ thống gặp vấn đề nghiêm trọng"
    
    fields = [
        {"name": "Thời gian", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": False}
    ]
    
    if metrics:
        for key, value in metrics.items():
            fields.append({"name": key, "value": str(value), "inline": True})
    
    return send_discord_embed(
        title=title,
        description=description,
        color=color,
        fields=fields,
        footer="VIP Key System - Health Check"
    )


def log_coupon_used(coupon_code, uid, discount, period):
    """Log khi coupon được sử dụng"""
    period_names = {"1d": "1 ngày", "7d": "7 ngày", "30d": "30 ngày", "90d": "90 ngày"}
    period_display = period_names.get(period, period)
    
    return send_discord_embed(
        title="🎫 Coupon Sử Dụng",
        description=f"Mã giảm giá đã được áp dụng",
        color=0xf1c40f,  # Yellow/Gold
        fields=[
            {"name": "Mã", "value": f"`{coupon_code}`", "inline": True},
            {"name": "UID", "value": f"`{uid}`", "inline": True},
            {"name": "Giảm giá", "value": f"{discount}%", "inline": True},
            {"name": "Gói", "value": period_display, "inline": True},
            {"name": "Thời gian", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": False}
        ],
        footer="VIP Key System - Coupon Tracking"
    )


def log_autosync(sync_types, success_count=0, failed_count=0, interval_minutes=5):
    """Log khi auto-sync được thực hiện"""
    
    # Tạo danh sách các loại data đã sync
    sync_list = "\n".join([f"• {dtype}" for dtype in sync_types])
    
    # Xác định màu dựa trên kết quả
    if failed_count == 0:
        color = 0x2ecc71  # Green - Success
        status_emoji = "✅"
        status_text = "Hoàn tất"
    elif success_count > 0:
        color = 0xf39c12  # Orange - Partial success
        status_emoji = "⚠️"
        status_text = "Một phần"
    else:
        color = 0xe74c3c  # Red - Failed
        status_emoji = "❌"
        status_text = "Thất bại"
    
    fields = [
        {"name": "Trạng thái", "value": f"{status_emoji} {status_text}", "inline": True},
        {"name": "Khoảng thời gian", "value": f"{interval_minutes} phút", "inline": True},
        {"name": "Thời gian", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": False}
    ]
    
    if sync_types:
        fields.append({"name": "Loại data đã sync", "value": sync_list, "inline": False})
    
    if success_count > 0 or failed_count > 0:
        result = f"Thành công: {success_count}"
        if failed_count > 0:
            result += f" | Thất bại: {failed_count}"
        fields.append({"name": "Kết quả", "value": result, "inline": False})
    
    return send_discord_embed(
        title="🔄 Auto-Sync Hoàn Tất",
        description="Tự động đồng bộ dữ liệu từ GitHub",
        color=color,
        fields=fields,
        footer="VIP Key System - Auto-Sync",
        webhook_url=WEBHOOK_SYNC_URL
    )


# Test function
if __name__ == "__main__":
    print("Testing Discord webhook...")
    log_order_created("TEST123456")
    print("\nWebhook test completed!")
