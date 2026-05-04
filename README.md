# AI Image Tool 🖼️

Remove backgrounds and upscale images with one click. Drag & drop interface.

## Features
- **Background Removal**: Remove backgrounds from any image (uses `rembg` library)
- **2x Upscaling**: Double image resolution with LANCZOS resampling
- **Combined Mode**: Remove background AND upscale in one operation
- **Drag & Drop**: Modern upload interface
- **Stripe Payments**: Credit packs and subscriptions

## Pricing
- 5 Credits: $14.90 ($2.98/image)
- Pro Monthly: $19.99/month (unlimited)

## Setup
```bash
pip install -r requirements.txt
# rembg requires onnxruntime - may take a moment on first run
export STRIPE_PUBLISHABLE_KEY=pk_test_...
export STRIPE_SECRET_KEY=sk_test_...
gunicorn app:app
```

## Stack
- Flask (Python)
- rembg (AI background removal)
- Pillow (image processing)
- Stripe Checkout
