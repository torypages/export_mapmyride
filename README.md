# Export TCX file from MapMyRide.com

* Just a script to download all the TCX files for your workouts.
* Edit `bottom_year` if your workouts extend into 2011 or beyond, or much earlier.
* Will get workouts from now until but excluding the `bottom_year`
* Uses Selenium, see `requirements.txt`
* Downloads and uses adblock for Firefox. I'd love to not do this, but the ads were causing too many problems. Additionally there are pop-up ads which I don't mind blocking.
* Saves TCX files to the same path as the script inside a folder called tcx_files
* Credentials are stored in credentials.txt. Replace the placeholders with yours.
* First gets all the urls to your workouts, then saves them to a file for safe keeping then downloads all the TCX files.
* This file (mentioned above) is `workouturls.txt` if it exists the script will only try and download the TCX files.
* Script will not re-download existing TCX files.

* I hope MapMyRide.com doesn't mind this. They shouldn't. If they do, that will be one quick way to get me to leave their service. People should always be able to extract their data.

* Please use this script responsibly.

* The most interesting part about this script to me is that I take the cookies from Selenium then I use them with urllib. That's cool.
