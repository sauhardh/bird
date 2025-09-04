
# bird 🐦

> a news-poster bot on X
> -


**How does it do what it does?**
- Takes the news from `RSS` feed from news' website.
- Uses `Groq` AI's API for filtering "viral-potential" news.
- Search image related to that topic on either Image search of `Brave` or `DuckDuckGo`
- Image processing -> Overlay the headline of news on the Image downlaoded
- With some care of `exception`, it is sent to X's API for posting.
- Updates the Timer on `time.txt` to filter out the old news.

> **Note**:
> X hates "bot" accounts and actively supress such account from reaching the audience.
> They will also "permanently" ban such account. 
