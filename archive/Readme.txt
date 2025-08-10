----------------------------------------------------------------
----------------------------------------------------------------

    VMDSizing Local Edition

    ver5.01.08 EN

                                    miu200521358
                            translated by Ulyssa

----------------------------------------------------------------
----------------------------------------------------------------

Thank you for downloading my tool.
Please check the following before use.

----------------------------------------------------------------


----------------------------------------------------------------
■ Overview
----------------------------------------------------------------

This tool resynthesizes VMD (MMD motion data) to fit the specified model's proportions.

----------------------------------------------------------------
■ Distribution Videos
----------------------------------------------------------------

■ Added support for multi-person motions and stance correction to VMD Sizing [ver5.00]
https://www.nicovideo.jp/watch/sm37143852

■ Made VMD Sizing faster, more reliable, and safer [ver5.01]
https://www.nicovideo.jp/watch/sm37848503

■ Content Tree Illustration
https://seiga.nicovideo.jp/seiga/im9755721

----------------------------------------------------------------
■ Included Files
----------------------------------------------------------------

・VMDSizing_5.01.08_64bit.exe ... Main tool (only 64bit version since ver5.00)
・Readme.txt                  ... This readme
・VMD Sizing Wiki             ... Link to Wiki
・Content Tree Illustration   ... Link to content tree illustration
・Bulk Sizing Sample.csv      ... Sample CSV for bulk sizing
・Morph Replacement Sample    ... Sample collection for morph replacement (see inside for details)

----------------------------------------------------------------
■ System Requirements
----------------------------------------------------------------

Windows8.1/10/11 64bit (tested only on Windows 11)

----------------------------------------------------------------
■ Startup
----------------------------------------------------------------

・Basically, just run the exe directly.

・High-spec version performs parallel processing internally, making it about 1.3 times faster than the normal version.
However, it also increases the load, so it's recommended only for those with capable PCs.

・Log version outputs a log file in the same location as the output VMD file, as in v4.

・File history can be copied by placing "history.json" in the same directory as the exe.

----------------------------------------------------------------
■ Sizing Features
----------------------------------------------------------------

1) Basic Features

Processing performed when sizing without any options.

・Scale Correction
  ... Adjusts the positions of movement-related bones to match the scale of the source model to the target model.
      (Master, Center, Groove, Leg IK Parent, Leg IK, Toe IK)

      * Supports multi-person motions

      ・By adding file sets (VMD, source model, target model) in the "Multi" tab, you can bulk size multi-person motions.
        When bulk sizing multi-person motions, the movement scale ratios are unified for all, preserving formations.
        Position alignment and camera are also supported for multiple people.

・Arm Stance Correction
  ... Aligns the arm angles of the source and target models.
      However, if either model includes Arm IK, correction is not performed unless the "Skip Check" checkbox in the "Arm" tab is ON.
      (If the skip checkbox is ON, forced correction is possible)

      * Handling of Arm IK
        ・Arm IK is used for various purposes depending on the model, such as assisting arm direction or clothing, so mechanical judgment is not possible.
          Therefore, models containing 腕IK/うでIK/腕ＩＫ/うでＩＫ, etc. are excluded from arm processing in sizing.
          In many cases, sizing may work fine as is, so try basic sizing first and if it doesn't work, you may give up.

----------------
3) Supported File Extensions for Source Motion

・VMD files (motion)
・VPD files (pose)

You can bulk process all matching files in a folder by replacing part of the file name with an asterisk (*).
* Only the "Target Motion VMD/VPD" field in the "File" tab supports asterisks.
* Source and target models can only be specified one at a time (motion is switched for the same combination).
* Output files are VMD only.

----------------
4) Additional Stance Corrections

Processing performed by turning ON the "Add Stance Correction" checkbox in the "File" or "Multi" tab.
You can select/deselect stance corrections using the "*" button next to the checkbox.

・センターXZスタンス補正/Center XZ Stance Correction
  ... Adjusts the center of gravity (center position) to match the source model.
      Especially effective for ballet turns and rotations with extended core.

・上半身補正/Upper Body Correction
  ... Adjusts the upper body and upper body 2 (if present) so the head position matches the source model.
      Effective for motions involving bending or stretching.
      Quadruped models composed of semi-standard bones will stand upright.

・下半身補正/Lower Body Correction
  ... Adjusts the lower body so the midpoint of the legs matches the source model.
      Quadruped models composed of semi-standard bones will stand upright.

・つま先ＩＫ補正/Toe IK Correction
  ... Converts toe IK movement to leg IK rotation (toe IK values are reset).
      Effective for motions using toe IK.

・足ＩＫ補正/Leg IK Correction
  ... Adjusts leg IK so its position relative to the leg bone matches the source model.
      Effective for small models like Nendoroid.
      Since ver5.01.02, this is OFF by default (legs may slip slightly).

・つま先補正/Toe Correction
  ... Adjusts the toe position from the floor to match the source model.
      Considers Toe EX (toe IK is a bit tricky).

・肩補正/Shoulder Correction
  ... Adjusts shoulder and shoulder P (if present) to match the initial stance tilt of the source model.
      Makes dynamic motions with large shoulder movements.
      * shoulder P values are converted to shoulder (shoulder P values are reset).

・センターY補正/Center Y Correction
  ... Adjusts the center so the arm's distance from the floor matches the source model.
      Part of the floor position alignment up to v4.

----------------
5) Twist Distribution Correction

Processing performed by turning ON the "With Twist Distribution" checkbox in the "File" or "Multi" tab.

  ・Arm twist:  Applies twist for arm X, elbow X, elbow Z
  ・Hand twist: Applies twist for wrist X
  ・Elbow:      Applies only local Y rotation for elbow (makes elbow deformation cleaner)

・Even if twist is already present, distribution processing is performed considering it.
However, due to the nature of twist, processing is done per keyframe at change points, so it takes time.

----------------
6) Morph Replacement

You can replace any morph in the source motion with any morph in the target model.
Morph size can also be corrected.
Morphs can be specified per file set.
If A→B and B→C are specified at once, B will have A+B correction, and C will have B's correction.

----------------
7) Arm Processing

Both collision avoidance and position alignment can be processed (collision avoidance → position alignment in order).
As with arm stance correction, if Arm IK is present, processing is not performed, so turn ON the skip option if you want processing.
Collision avoidance includes rigid body selection, so model loading is performed when switching tabs.

・Collision Avoidance
  ... Avoids collision when the specified bone-following rigid body and hand collide.
      You can easily add bone-following rigid bodies in PMX Editor (PmxView > Edit > Select Bone > Create Basic Rigid Body - Bone Following Rigid Body).
      Hand detection points: fingertip, wrist, midpoint between wrist and elbow, elbow, midpoint between arm and elbow (5 points).

・Position Alignment
  ... Aligns wrist (or finger) position to the source model.
      For multi-person motions, aligns positions between people. Height differences are interpolated appropriately.

      ・Finger Position Alignment: Aligns not only wrists but also finger positions.
                            For multi-person motions, this takes time and may not look good, so a warning is shown.

      ・Floor Position Alignment: Aligns not only wrists but also with the floor position.

----------------
8) Leg Processing (since ver5.01.06)

・Movement Correction
  ... Used when you want to expand overall movement in multi-person motions, make movements more dynamic, or suppress them.
      It's a ratio, so the default is "1". "1.1" means "1.1 times".

・Leg IK Offset
  ... Used when legs overlap when closed (due to thickness), or when you want to adjust only individual leg IK movement without changing overall movement.
      This is the actual coordinate size, so "+0.1" widens the left/right legs by 0.1 in the X direction ("-0.1" narrows).

----------------
9) Camera Processing

Adjusts the camera so it matches the appearance of the source model.
For multi-person motions, height differences are interpolated when focusing on individuals.
If there are large height differences and many people, there may be slight misalignment. Adjusting the field of view often helps.
You can specify the camera source model per file set.
Since ver5.01.05, adjustments are made to reduce conversion misalignment when the source model has only bones.

----------------------------------------------------------------
■ Bulk Sizing Feature
----------------------------------------------------------------

You can bulk size multiple motions by specifying a CSV in the "Bulk" tab.
See "Bulk Sizing Sample.csv" for details.
The first header row is skipped.

* Do not use commas in data
* Output data is saved in the same location as the original VMD file, same as GUI default.
* Notes for opening in LibreOffice:
  ・In the text import dialog, uncheck "semicolon" in the delimiter options.

01st column ... Group No
          Assign consecutive numbers per group you want to size.
02nd column ... Target Motion VMD/VPD (full path)
          File path for "Target Motion VMD/VPD" in "File"/"Multi" tab. Asterisks not allowed.
03rd column ... Source Model PMX
          File path for "Source Model PMX" in "File"/"Multi" tab.
04th column ... Destination Model PMX
          File path for "Destination Model PMX" in "File"/"Multi" tab.
05th column ... Center XZ Correction
          Checkbox for "Add Stance Correction > Center XZ Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
06th column ... Upper Body Correction
          Checkbox for "Add Stance Correction > Upper Body Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
07th column ... Lower Body Correction
          Checkbox for "Add Stance Correction > Lower Body Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
08th column ... Leg IK Correction
          Checkbox for "Add Stance Correction > Leg IK Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
09th column ... Toe Correction
          Checkbox for "Add Stance Correction > Toe Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
10th column ... Toe IK Correction
          Checkbox for "Add Stance Correction > Toe IK Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
11th column ... Shoulder Correction
          Checkbox for "Add Stance Correction > Shoulder Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
12th column ... Center Y Correction
          Checkbox for "Add Stance Correction > Center Y Correction" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
13th column ... Twist Distribution
          Checkbox for "Twist Distribution" in "File"/"Multi" tab. Must be 0:Disabled or 1:Enabled.
14th column ... Morph Replacement
          Set for "Morph Replacement" in "Morph" tab. Use "Source Morph:Target Morph:Size;" for each set.
          (Cannot use semicolons in morph names. Final semicolon is required.)
15th column ... Collision Avoidance
          Checkbox for "Collision Avoidance" in "Arm" tab. Must be 0:Disabled or 1:Enabled.
16th column ... Collision Avoidance Rigid Body
          List of target rigid body names for "Collision Avoidance" in "Arm" tab. Connect with semicolons like "RigidBodyName;".
          (Cannot use semicolons in rigid body names. Final semicolon is required.)
17th column ... Position Alignment
          Checkbox for "Position Alignment" in "Arm" tab. Must be 0:Disabled or 1:Enabled.
18th column ... Finger Position Alignment
          Checkbox for "Align by finger position" in "Arm" tab. Must be 0:Disabled or 1:Enabled.
          Forced to 0 for multi-person motions.
19th column ... Floor Position Alignment
          Checkbox for "Also align with floor" in "Arm" tab. Must be 0:Disabled or 1:Enabled.
20th column ... Wrist Distance
          Slider for "Wrist Distance" in "Arm" tab. Must be 0 or greater. GUI default is "1.7" for single person, "2.5" for multiple.
21st column ... Finger Distance
          Slider for "Finger Distance" in "Arm" tab. Must be 0 or greater. GUI default is "1.4".
22nd column ... Floor Distance
          Slider for "Wrist to Floor Distance" in "Arm" tab. Must be 0 or greater. GUI default is "1.2".
23rd column ... Arm Check Skip
          Checkbox for "Skip arm-to-wrist sizing check" in "Arm" tab. Must be 0:Disabled or 1:Enabled.
24th column ... Overall Movement Correction Value
          Slider for "Overall Movement Correction" in "Leg" tab. GUI default is "1".
25th column ... Leg IK Offset
          Slider for "Leg IK Offset" in "Leg" tab. GUI default is "0".
26th column ... Camera Motion VMD
          File path for "Camera Motion VMD" in "Camera" tab. Only the first row per group is referenced.
27th column ... Distance Movable Range
          Slider for "Distance Movable Range" in "Camera" tab. Must be 1 or greater.
28th column ... Camera Source Model PMX
          File path for "Camera Source Model PMX" in "Camera" tab.
29th column ... Overall Y Offset
          "Overall Y Offset" in "Camera" tab.

----------------------------------------------------------------
■ Extra Features
----------------------------------------------------------------

1) CSV Output

・Outputs specified VMD motion data in CSV format.
・Separate formats for bones, morphs, and camera.
・Outputs all interpolation curves as well.

----------------
2) VMD Output

・Outputs specified CSV data (following CSV output format) as VMD motion data.
・Outputs all interpolation curves as well.

* Smoothing, morph blend, and interpolation curve viewer have been moved to MotionSupporter.

----------------------------------------------------------------
■ Detailed Usage
----------------------------------------------------------------

https://github.com/miu200521358/vmd_sizing/wiki/02.-使い方

Usage instructions, explanations, FAQ, and how to handle cases where the source model cannot be found are posted on the Wiki as needed.

----------------------------------------------------------------
■ If Problems Occur
----------------------------------------------------------------

・Garbled file name after extraction
・Detected as a virus by McAfee
If you encounter such problems, please refer to the following page to see if you can resolve them.

https://github.com/miu200521358/vmd_sizing/wiki/03.-問題が起きた場合

If you still cannot resolve the issue, please report it in the community.

----------------------------------------------------------------
■ Community Information
----------------------------------------------------------------

NicoNico Community: https://com.nicovideo.jp/community/co5387214

  Lab for various experiments related to VMDSizing and MotionSupporter tools.
  You can try beta versions early.
  I hope to provide support if sizing doesn't work well.
  It's closed, but auto-approved, so feel free to join.

----------------------------------------------------------------
■ Terms of Use, etc.
----------------------------------------------------------------

[Required]

・If you publish/distribute converted VMD motion results, please credit.
・For NicoNico videos, please register the content tree illustration (im9755721) in the content tree.
* If you register in the content tree, crediting is optional.

[Optional]

Within the scope of the original motion's terms, you are free to do the following with this tool and generated motions:

・Adjust/modify motions
・Post videos using motions to video sites, social media, etc.
  ・You may post generated motions as-is for progress, etc.
  ・However, if the original motion/model's terms specify conditions for posting or age restrictions, motions generated with this tool must also comply.

[Prohibited]

Please refrain from the following with this tool and generated motions:

・Actions outside the scope of the original motion/model's terms
・Claiming complete authorship of motions
・Actions that cause inconvenience to rights holders
・Use for slander or defamation of others (2D/3D not limited)

* Since ver4.02, the following is no longer prohibited:
  "Use in works containing excessive violence, obscenity, romance, grotesque, political, or religious expression (R-15 or higher)"

  ・Please be sure to check the scope of the original motion/model's terms before use.
  ・When publishing works, please consider measures to avoid search exposure, etc.

* Since ver5.00, the following is no longer prohibited:
  "Commercial use"

[Disclaimer]

・Movements may change from the original motion, so use at your own risk.
・The author is not responsible for any problems caused by the use of the tool.

----------------------------------------------------------------
■ Source Code & Libraries
----------------------------------------------------------------

This tool is created in Python and uses/includes the following libraries:

・numpy (https://pypi.org/project/numpy/)
・bezier (https://pypi.org/project/bezier/)
・numpy-quaternion (https://pypi.org/project/numpy-quaternion/)
・wxPython (https://pypi.org/project/wxPython/)
・pyinstaller (https://pypi.org/project/PyInstaller/)

Source code is published on Github (MIT License):

https://github.com/miu200521358/vmd_sizing


----------------------------------------------------------------
■ Credits
----------------------------------------------------------------

Tool name: VMDSizing
Author: miu or miu200521358

http://www.nicovideo.jp/user/2776342
Twitter: @miu200521358
Mail: garnet200521358@gmail.com

----------------------------------------------------------------
■ History
----------------------------------------------------------------

ver5.01.08 (2022/11/19)
    ・Bugfix:
        ・Added a condition to insert 1 when all values are 0 during quaternion normalization (isnan check), to prevent nan in matrix calculation
        ・Fixed camera sizing previous keyframe copy judgment not working properly

ver5.01.07 (2022/07/18)
    ・Bugfix:
        ・Removed default scalar=1 in quaternion normalization (isnan check)
          * Only occurs when vpd has Y=180 (0.000000,1.000000,0.000000,-0.000000;)

ver5.01.06 (2022/04/19)
    ・Feature: Added Leg tab
        ・movement correction: For expanding overall movement in multi-person motions, making movements more dynamic, etc.
        ・Leg IK offset: For adjusting only individual leg IK movement when legs overlap when closed, etc.
    ・Feature: Added "Save Bulk Sizing" button to Bulk tab
        ・Outputs current sizing settings to CSV
        ・Loading the output CSV in the Bulk tab allows repeated use of sizing settings
    ・Bugfix:
        ・Fixed output VMD file name not converting properly during continuous sizing
        ・Fixed camera VMD CSV output not outputting rotation info correctly

ver5.01.05 (2022/02/11)
    ・Feature: Added processing to display missing bones as semi-standard and others during pre-check
    ・Feature: When source model has only bones, camera sizing now references estimated bone position instead of vertex position
    ・Feature: Added error messages

ver5.01.04 (2021/09/23)
    ・Bugfix: Fixed error when reading VMD data without morph block
    ・Feature: Added camera sizing only option
    ・Feature: Changed background to pale blue-green when spin scroll is negative
        ・Morph replacement: size correction field
        ・Camera correction: Y offset

ver5.01.03 (2021/06/30)
    ・Feature: Added processing to check bone properties when checking for missing bones before conversion
        → Easier to see when D bones are present but disabled
    ・Change: Position alignment
        ・Excludes elbow from position alignment arm IK processing if elbow angle is less than 30 degrees
          → Should reduce possibility of elbow breaking backwards
    ・Change: Arm stance correction
        ・Adjusted processing to avoid wrist breaking for ISAO-style Miku
          (For ISAO-style Miku, wrist and middle finger are separated, so adjustment is based on display destination)

ver5.01.02 (2021/05/04)
    ・Spec change: Default OFF for "Leg IK Correction" in additional stance correction for normal body types (legs may slip)
    ・Bugfix: Fixed quaternion multiplication order in IK calculation (improved accuracy for position alignment/collision avoidance)
    ・Bugfix: Additional stance correction
        ・Shoulder correction: adjusted calculation threshold
        ・Center Y correction: fixed offset calculation
    ・Bugfix: Collision avoidance
        ・Made avoidance frame for midpoint between arm and elbow slightly smaller
        ・Adjusted elbow cancel from 10 to 30 degrees (should reduce breaking)
        ・Adjusted balance with position alignment
    ・Bugfix: Camera correction
        ・Fixed occasional calculation bug with zero-distance camera (now calculated with 0.00001 internally)
        ・Cythonized (should be a few seconds faster)

ver5.01.01 (2020/12/20)
    ・Bugfix: Fixed failure to overwrite morph replacement in multi-person sizing

ver5.01 (2020/11/21)
    ・Processing speed up (about 30% faster)
    ・Added progress status display
    ・Added bulk sizing feature
    ・Improved twist distribution accuracy
    ・Added distance movable range limit option to camera sizing
    ・Moved smoothing, morph blend, and interpolation curve viewer to MotionSupporter
    ・Bugfix: Fixed occasional distance (scale ratio) bug in camera sizing
    ・Bugfix: Fixed failure when aligning vpd
    ・Bugfix: Fixed error when collision avoidance was specified for head bone with no weighted vertices

ver5.00 (2020/07/05)
    ・Rebuilt using numpy instead of PyQt5 for math library
    ・Added support for multi-person motions
    ・Added additional stance correction
    ・Added twist distribution feature
    ・Added smoothing feature
    ・Added morph blend feature

ver4.05 (2020/02/22)
    ・Adjusted binary structure for faster VMD loading during output
    ・Added sound on sizing completion (Windows INFO sound)
    ・Fixed file button with history to open folder of first history file when "Open" is clicked

ver4.04 (2019/12/10)
    ・Bugfix: Fixed "unexpected error" with floor position alignment option

ver4.03 (2019/12/04)
    ・Added "Finger Position Alignment" option for finger tutting motions
    ・Adjusted processing for floor position alignment option
    ・Internalized center up/down parameter for floor position alignment option
    ・Bugfix: Fixed "unexpected error" with floor position alignment option

ver4.02 (2019/11/17)
    ・Externalized wrist/foot to floor distance adjustment parameters for floor position alignment option
    ・Added warning message for infinite loop error when traversing parent bones with circular reference
    ・Bugfix: Fixed error when model name contains non-Japanese/English (cp932) characters

ver4.01 (2019/10/29)
    ・Bugfix: Fixed crash when specifying model without "Center" as target

ver4.00 (2019/10/25)
    ・Added camera sizing feature
    ・Added floor position alignment option
    ・Added toe position alignment feature
    ・Added VMD converter feature
    ・Bugfix: Fixed calculation formula for center of gravity correction

ver3.00 (2019/07/26)
    ・Changed UI to tab format
    ・Added wrist position alignment processing
    ・Added arm stance adjustment processing
    ・Changed morph replacement processing (now supports split/merge)
    ・Changed movement bone scale ratio
    ・Added CSV converter feature
    ・Bugfix: Added leg IK parent to adjustment targets, fixed hand position estimation in collision avoidance

ver2.03 (2019/06/05)
    ・Added center of gravity adjustment offset processing
    ・Added processing to display model name when specifying VMD file
    ・Added processing to output target model name when outputting VMD file
    ・Bugfix: Excluded unnecessary output in missing bone/morph check

ver2.02 (2019/06/02)
    ・Changed all parent bones to sizing targets
    ・Added dropdown to select collision avoidance detection point (index finger or wrist)
    ・Bugfix: Fixed bug where elbow sometimes flipped

ver2.01 (2019/05/29)
    ・Added morph replacement feature

ver2.00 (2019/05/26)
    ・Started general distribution of local version

ver1.10
    ・Started test distribution of local version

ver1.00
    ・Started distribution of colab version




