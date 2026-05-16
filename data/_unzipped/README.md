# README 

This README should be used to clarify terms and information used in our results. Need help? Reach out to your dedicated project manager or contact@centaurlabs.com.

This is Centaur's primary data results format, and includes all information relevant to your labeling results. Here are the definitions of the column names in the CSV:

#### IDENTIFIERS AND CASE STRUCTURE 
- Case ID: Unique identifier for cases in our system.
- Origin: Original file identifier or filepath.
- Origin Created At: Date and time file was uploaded to our system.
- Content ID: Unique identifier for the content (e.g. image, text, audio, etc.) in the case.
- URL: Click this URL to view the case in our system.
- Labeling State: Click the information icon next to “Status” to see the definitions of labeling states.
- Series (if applicable): Unique identifier for the video or content sequence (e.g. image frames) that the case is associated with.  A series can contain multiple cases, and a case can cover part or all of a series.
- Series Index (if applicable): Unique identifier for the content as part of its series (e.g. image frames).
- Patch (if applicable): Area of interest on an image to be annotated for the case, in WKT format with coordinates rescaled to a 0-100 scale.

#### READS AND ANNOTATIONS
- Qualified Reads: Number of reads (“opinions”) on the case. Qualified Reads are those which meet a predefined accuracy criterion.
- Correct Label: If Gold Standard case, the label as assigned by you and/or an admin. If Labeled case, the Majority Label when the case has received the required number of Qualified Reads.
- Majority Label: Label chosen by the majority of Qualified Reads.

#### MEASURES OF CONFIDENCE
- Difficulty: Qualified Reads without the Correct Label divided by total Qualified Reads.
- Agreement: Qualified Reads with the Majority Label divided by total Qualified Reads.
- Nth Choice Answer: Nth most chosen answer of available answer choices.
- Nth Choice Votes: Number of Qualified Reads having the Nth choice answer.
- Nth Choice Weight: Sum of all accuracy scores of Qualified Reads having the Nth Choice Answer.

#### OTHER INFORMATION
- Internal Notes: Any notes internal to your team or tracked by Centaur relevant to the case.
- Comments: Flags or comments on the case by our labelers.
- Explanation: Notes written by you and/or an admin to help train and educate labelers. The explanation is shown to labelers after they have submitted a read.