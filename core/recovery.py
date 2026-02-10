import os
import shutil
import time

class ShadowVault:
    def __init__(self, monitored_folder):
        self.monitored_folder = os.path.abspath(monitored_folder)
        
        # 1. DEFINE THE ONE TRUE VAULT
        self.vault_folder = os.path.join(os.path.dirname(self.monitored_folder), ".AegisVault")
        self.old_vault = os.path.join(os.path.dirname(self.monitored_folder), ".aegis_vault")

        # 2. AUTO-CLEANUP: Delete the duplicate/old vault if it exists
        if os.path.exists(self.old_vault):
            print(f"🧹 Removing duplicate vault: {self.old_vault}")
            try:
                shutil.rmtree(self.old_vault)
            except Exception as e:
                print(f"⚠️ Could not remove old vault: {e}")

        # 3. Create the correct vault if missing
        if not os.path.exists(self.vault_folder):
            os.makedirs(self.vault_folder)
            # Hide it on Windows
            try: os.system(f'attrib +h "{self.vault_folder}"')
            except: pass

    def create_snapshot(self):
        """Takes a clean backup. MUST BE RUN WHEN FILES ARE SAFE."""
        try:
            # Clear previous backup to avoid mixing old/new files
            for filename in os.listdir(self.vault_folder):
                file_path = os.path.join(self.vault_folder, filename)
                try:
                    if os.path.isfile(file_path): os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except: pass

            # Copy current files
            files = os.listdir(self.monitored_folder)
            count = 0
            for file in files:
                src = os.path.join(self.monitored_folder, file)
                dst = os.path.join(self.vault_folder, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    count += 1
            
            print(f"✅ SNAPSHOT CREATED: {count} files secured in .AegisVault")
            return True
        except Exception as e:
            print(f"❌ Backup Failed: {e}")
            return False

    def restore_snapshot(self):
        """Wipes infected files and restores the clean snapshot."""
        try:
            print("⏳ Wiping Infected Zone...")
            
            # 1. NUKE THE INFECTED ZONE (Delete everything)
            for filename in os.listdir(self.monitored_folder):
                file_path = os.path.join(self.monitored_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"⚠️ Failed to delete: {filename} (might be in use)")

            # 2. RESTORE FROM VAULT
            print("⏳ Restoring Clean Files...")
            files = os.listdir(self.vault_folder)
            count = 0
            for file in files:
                src = os.path.join(self.vault_folder, file)
                dst = os.path.join(self.monitored_folder, file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    count += 1
            
            print(f"✅ ROLLBACK SUCCESSFUL: {count} files restored.")
            return True
        except Exception as e:
            print(f"❌ Rollback Failed: {e}")
            return False