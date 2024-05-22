RTAEbayTool
===========
# Directions
**Follow carefully :D**

Step 1: Fill out your inventory spreadsheet. Once completed, this sheet will provide all of the information needed to upload your listings in the below steps.
(Double check your spreadsheet before creating a payload file. It is very important to ensure that you enter your data correctly.)

---

Step 2: After taking photos of your items, click the "Rename Photos" button. This will open a new window where you will be asked to enter a Suffix, Starting Number, and # of Photos. Review the table below to understand the entry fields. 
Click "Rename Photos" and it will ask you to select the folder where your photos are located. Select that folder, and hit ok.
After you have renamed your photos, you can close this window.
| Entry Field   | Example Entry | Explanation |
| ------------- | ------------- | ----------- |
| Prefix  | RTA    | Designator, can be your initials |
| Starting Number | 10000 | The first SKU for the items you're listing |
| # Of Photos    | 2    | How many photos PER ITEM. Usually 2 |

---

Step 3: After renaming your photos, you'll click on "Upload Photos" button. This will open another window. At the bottom there will be a button that says "Upload Files," click it. This will open a File Explorer (or Finder for Mac). You will select the folder where you saved your photos (that were renamed in Step 2). This will upload your photos to Flickr, progress will be displayed in the terminal. Once this is done, you can close this window.

---

Step 4: After you have uploaded your photos you can hit the "Create Payload" button. This will open a file explorer asking you to find your spreadsheet **(aptly named "RTAEbayTool - {your name}.xlsx")**. Select that spreadsheet, and hit ok. When this is done it will tell you the file name and location in terminal. 

This will output the file to whichever location you have set in 
Settings > Set Default Paths > Default Output Directory
Best practice would be to open this file and double check that the data inside of it is correct and matches up appropriately, and to ensure that photo links were input into the payload spreadsheet correctly.

Photo links should end with .jpg (or whatever file type such as .png, ebay prefers .jpg) and links should be separated with a pipe character (" | ")

---

Step 5: Now you can go to ebay and follow these steps below to upload the file
| Step | Directions |
| --- | ---- |
| 1. | Go to "My Ebay > Selling" |
| 2. | Go to "Reports > Uploads" |
| 3. | Click the "Upload Template" Button |
| 4. | Select the payload file |
| 5. | Your listing should be live now|

If you encounter an error, from the Reports page you can down the results of the upload and it will provide a spreadsheet detailing what each error was and sometimes recommendations. You can modify the payload spreadsheet to resolve these errors and attempt again. 

---

Any issues or errors please leave them on the GitHub page.
https://github.com/FCCBLuurr/RTAEbayTool/issues

Provide as much detail as possible, and steps that you performed to encounter this error. The more information the better I will be able to fix the issue.

---

Notes:
After clicking on one of the buttons and a new window appears, you will be unable to interact with the main app window. 