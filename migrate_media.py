import os
import django
import cloudinary.uploader

# 1. Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

# 2. Point to your local media folder
# Using absolute path to be safe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

def upload_files(dir_path):
    if not os.path.exists(dir_path):
        print(f"Error: {dir_path} does not exist!")
        return

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # Full path to the local file
            local_path = os.path.join(root, file)
            
            # Calculate the path relative to 'media' (e.g., 'qr_codes/image.png')
            relative_path = os.path.relpath(local_path, dir_path)
            
            # Clean up path for Cloudinary (replaces backslashes on Windows)
            cloudinary_path = relative_path.replace("\\", "/")
            
            print(f"Uploading: {cloudinary_path}...")
            
            try:
                cloudinary.uploader.upload(
                    local_path,
                    # This keeps your subfolder structure intact in the cloud
                    public_id=cloudinary_path.rsplit('.', 1)[0],
                    folder="media" 
                )
            except Exception as e:
                print(f"Failed to upload {file}: {e}")

if __name__ == "__main__":
    upload_files(MEDIA_DIR)
    print("--- Finished Uploading ---")