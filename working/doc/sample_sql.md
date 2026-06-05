## 顯示所有 Percy Jackson and the Lightning Thief (Book 1) 的劃線
SELECT Text,
       COUNT(*) AS cnt
FROM Bookmark
WHERE VolumeID='2fd368fb-5353-436d-b60a-e7c326444408'
  AND Text IS NOT NULL
GROUP BY Text
ORDER BY cnt DESC, Text;



## 顯示所有書籍的 ID 和書名
sqlite> SELECT DISTINCT
   ...>        b.VolumeID AS BookID,
   ...>        c.BookTitle
   ...> FROM Bookmark b
   ...> JOIN content c
   ...>     ON b.VolumeID = c.BookID
   ...> WHERE b.Text IS NOT NULL
   ...>   AND c.BookTitle IS NOT NULL;

08edc68f-c2c4-40b4-afb0-212253c0b881|Hier encore, c'était l'été
10f75cf0-19bb-4bff-be42-b36fe51f4d8c|Harry Potter et la Chambre des Secrets
2c9ceed2-a7ed-4bd6-b99c-41bbe5b22225|Le Comte de Monte-Cristo
2fd368fb-5353-436d-b60a-e7c326444408|Percy Jackson and the Lightning Thief (Book 1)
7121c4ce-d664-4a1a-8751-099891a80aff|Harry Potter and the Chamber of Secrets
961be081-5a0a-4851-88db-26c7a4f1f544|Grammatik aktiv - Deutsch als Fremdsprache - 2. aktualisierteAusgabe - A1-B1
ddb9b6a1-d269-452e-ae93-1b8e4817e170|German Your Complete Guide to German Language Learning
e1497226-dab8-4f3b-b87d-1389a633a2d3|L'étranger
file:///mnt/onboard/Riordan, Rick/Percy Jackson_ The Complete Series (Books 1, 2, 3, 4, 5) - Rick Riordan.kepub.epub|Percy Jackson: The Complete Series (Books 1, 2, 3, 4, 5)
file:///mnt/onboard/Sempe & Goscinny, Rene/vacances du petit Nicolas, Les - Sempe & Rene Goscinny.kepub.epub|Les vacances du petit Nicolas


## 從某本書列出所有章節
sqlite> SELECT ContentID,
   ...>        Title
   ...> FROM content
   ...> WHERE BookID='2fd368fb-5353-436d-b60a-e7c326444408';
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/cover.xhtml|xhtml/cover.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/brand_page.xhtml|xhtml/brand_page.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/about_the_author.xhtml|xhtml/about_the_author.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/title.xhtml|xhtml/title.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/nav.xhtml|xhtml/nav.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/dedication.xhtml|xhtml/dedication.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/preface.xhtml|xhtml/preface.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/acknowledgements.xhtml|xhtml/acknowledgements.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter001.xhtml|xhtml/chapter001.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter002.xhtml|xhtml/chapter002.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter003.xhtml|xhtml/chapter003.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter004.xhtml|xhtml/chapter004.xhtml
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!kobo-locked.html12|kobo-locked.html
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/cover.xhtml-1|Cover
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html1-1|About the Author
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html2-1|Title Page
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/dedication.xhtml-1|Dedication
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/acknowledgements.xhtml-1|Acknowledgements
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter001.xhtml-1|1 • I Accidentally Vaporize My Pre-algebra Teacher
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter002.xhtml-1|2 • Three Old Ladies Knit the Socks of Death
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter003.xhtml-1|3 • Grover Unexpectedly Loses His Trousers
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter004.xhtml-1|4 • My Mother Teaches Me Bullfighting
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html9-1|5 • I Play Pinochle with a Horse
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html10-1|6 • I Become Supreme Lord of the Bathroom
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html11-1|7 • My Dinner Goes Up in Smoke
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html12-1|8 • We Capture a Flag
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html13-1|9 • I Am Offered a Quest
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html14-1|10 • I Ruin a Perfectly Good Bus
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html15-1|11 • We Visit the Garden Gnome Emporium
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html16-1|12 • We Get Advice from a Poodle
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html17-1|13 • I Plunge to My Death
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html18-1|14 • I Become a Known Fugitive
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html19-1|15 • A God Buys Us Cheeseburgers
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html20-1|16 • We Take a Zebra to Vegas
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html21-1|17 • We Shop for Waterbeds
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html22-1|18 • Annabeth Does Obedience School
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html23-1|19 • We Find Out the Truth, Sort Of
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html24-1|20 • I Battle My Jerk Relative
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html25-1|21 • I Settle My Tab
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html26-1|22 • The Prophecy Comes True
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html27-1|Read More
2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/EPUB/xhtml/EPUB/kobo-locked.html28-1|Copyright

## 顯示某本書某章所有的劃線 (chapter001.xhtml)
sqlite> SELECT Text
   ...> FROM Bookmark
   ...> WHERE ContentID='2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/ch01.xhtml'
   ...>   AND Text IS NOT NULL;
sqlite> SELECT Text
   ...> FROM Bookmark
   ...> WHERE ContentID='2fd368fb-5353-436d-b60a-e7c326444408!EPUB!xhtml/chapter001.xhtml'
   ...>   AND Text IS NOT NULL;
screech
scrawny
acne
shrivelled
talons
scythe
chaperone
decked
pelting
snatched
sphinx
deficit
dyslexia
doofuses
barfing
kleptomaniac
cuffs
sulphur
celery
 wads
stele
hag
spawn
sqlite> 