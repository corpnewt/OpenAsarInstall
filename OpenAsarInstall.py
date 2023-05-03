import platform, os, tempfile, json
from Scripts import downloader, utils

class OpenAsarInstall:
    def __init__(self, **kwargs):
        self.u = utils.Utils("OpenAsar Install")
        self.d = downloader.Downloader()
        self.url = "https://github.com/GooseMod/OpenAsar/releases/download/nightly/app.asar"
        self.size_limit = 4000000

    def get_asar_locations(self):
        path_list = []
        if platform.system().lower() == "darwin": # On macOS
            for discord,folder_name in (("Discord.app","discord"),("Discord PTB.app","discordptb"),("Discord Canary.app","discordcanary")):
                check_path = os.path.join("/Applications",discord,"Contents","Resources","app.asar")
                if os.path.isfile(check_path):
                    size = os.path.getsize(check_path)
                    settings_path = os.path.expanduser("~/Library/Application Support/{}/settings.json".format(folder_name))
                    path_list.append((discord,check_path,settings_path,size))
        elif os.name == "nt": # Got Windows
            for discord,folder_name in (("Discord","app-1.0.9012"),("DiscordPTB","app-1.0.1027"),("DiscordCanary","app-1.0.60")):
                check_path = os.path.join(os.path.expandvars("%localappdata%"),discord,folder_name,"resources","app.asar")
                if os.path.isfile(check_path):
                    size = os.path.getsize(check_path)
                    settings_path = os.path.join(os.path.expandvars("%appdata%"),discord.lower(),"settings.json")
                    path_list.append((discord,check_path,settings_path,size))
        return path_list

    def show_error(self,message):
        print(message)
        print("")
        self.u.grab("Press [enter] to return...")

    def main(self):
        while True:
            path_list = self.get_asar_locations()
            self.u.head()
            print("")
            if not path_list:
                print(" - Discord not found in /Applications")
            else:
                print("Located Discord Apps:\n")
                for i,x in enumerate(path_list,start=1):
                    print("{}. {}{}".format(i,x[0]," (already patched)" if x[-1] < self.size_limit else ""))
            print("")
            print("Q. Quit")
            print("")
            menu = self.u.grab("Please select an option:  ")
            if not len(menu): continue
            if menu.lower() == "q": self.u.custom_quit()
            # Should have a value - let's qualify the index
            try:
                menu = int(menu)-1
                assert -1 < menu < len(path_list)
            except:
                continue
            self.u.head()
            print("")
            # Have a valid index
            target = path_list[menu]
            t_bak = target[1]+".bak"
            if target[-1] < self.size_limit:
                print("Reverting OpenAsar - checking for app.asar.bak...")
                # We're restoring a backup - make sure it exists
                if not os.path.isfile(t_bak):
                    self.show_error(" - Not found!  Nothing to roll back.")
                    continue
                # We have a backup file
                print(" - Located!")
                print("Removing app.asar...")
                try: os.remove(target[1])
                except Exception as e:
                    self.show_error(" - Failed!: {}".format(e))
                    continue
                print("Renaming app.asar.bak to app.asar...")
                try: os.rename(t_bak,target[1])
                except Exception as e:
                    self.show_error(" - Failed!: {}".format(e))
                    continue
                print("Checking for settings.json...")
                if os.path.isfile(target[2]):
                    print(" - Locating, loading...")
                    try: settings = json.load(open(target[2],"r"))
                    except Exception as e:
                        self.show_error(" - Failed: {}".format(e))
                        continue
                    if "openasar" in settings:
                        print(" - Removing openasar key...")
                        settings.pop("openasar",None)
                        print(" - Saving...")
                        try: json.dump(settings,open(target[2],"w"),indent=2)
                        except Exception as e:
                            self.show_error(" - Failed: {}".format(e))
                            continue
                    else:
                        print(" - No openasar key - leaving as-is...")
                else:
                    print(" - Not found - nothing to remove...")
                print("")
                print("Done.")
                print("")
                self.u.grab("Press [enter] to return...")
                continue
            else:
                print("Installing OpenAsar...")
                temp = tempfile.mkdtemp()
                print("Downloading nightly...")
                f_path = self.d.stream_to_file(self.url,os.path.join(temp,os.path.basename(self.url)),progress=False)
                if not f_path:
                    self.show_error(" - Failed to download!")
                    continue
                if os.path.isfile(t_bak):
                    print("Backup of app.asar already exists - removing...")
                    try: os.remove(t_bak)
                    except Exception as e:
                        self.show_error(" - Failed!: {}".format(e))
                        continue
                print("Renaming app.asar to app.asar.bak...")
                try: os.rename(target[1],t_bak)
                except Exception as e:
                    self.show_error(" - Failed: {}".format(e))
                    continue
                print("Moving nightly app.asar into place...")
                try: os.rename(f_path,target[1])
                except Exception as e:
                    self.show_error(" - Failed: {}".format(e))
                    continue
                print("")
                print("Done.")
                print("")
                self.u.grab("Press [enter] to return...")
                continue

if __name__ == "__main__":
    o = OpenAsarInstall()
    o.main()