# DiscordHelper

A python script to detect whether your discord was tempered with in any noticeable way.
## Functionnement

DiscordHelper will provide a fast analysis over known malwares and progress its analysis toward a complete sha1 checksum comparison against a known good installation.

If the integrity can't be verified, the helper will propose to upload a new database with all computed data as a new staple to compare to (this functionnality is mostly useful if you have a custom/modded Discord).

### Windows
DiscordHelper is configured to run every test and save the result in a folder named "DiscordHelper" in the same directory as the script.
This file, named test_results_found.json, contains a snapshot of your current installation. If you change its name to test_results.json, DiscordHelper will use this snapshot instead of the bundled databases. (This feature is mostly useful if you have a custom/modded Discord).

### What to do if the integrity can't be verified?
Open a new issue, upload the test_results_found.json file and any details surrounding the problem.

If this isn't a bug in DiscordHelper, you may want to reinstall Discord, and possibly your whole operating system.

# WARNING
Due to the evolutive nature of viruses, only a new, clean installation of DiscordHelper will warranty a total detection of all threats, since a virus will always try to temper all methods of detecting it.

# DISCLAMER
While this program aims to provide a complete coverage over Discord Threats, there are many ways to temper with discord that cannot be covered in this program, mainly side-dll tempering and all forms of RAT and keyloggers. DiscordHelper cannot and will not try to analyse the rest of your operating system, we leave this intrusive behaviour to other anti-viruses.

## Security and trust
We highly encourage all users to check, or have someone check our code.
We do not analyse the content of your data, we do not send any data to our servers, 
and we do not try to temper in any way to your install, even to fix it.

--------

```
  __ \  _)                              |  |   |        |                    
  |   |  |   __|   __|   _ \    __|  _` |  |   |   _ \  |  __ \    _ \   __| 
  |   |  | \__ \  (     (   |  |    (   |  ___ |   __/  |  |   |   __/  |    
 ____/  _| ____/ \___| \___/  _|   \__,_| _|  _| \___| _|  .__/  \___| _|    
                                                          _|   
```
