import pyodbc
from googleapiclient.discovery import build

# Define your API key and build the YouTube service
API_KEY = 'AIzaSyAb-wwet5h-PyyQtGB4Onm3IoO2tePg0BY'  # Replace this with your actual YouTube Data API v3 key
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Database credentials
server = 'OS'
database = 'FARMERSCHOICE'
username = 'sa'
password = 'Peter@1490'
driver = '{ODBC Driver 17 for SQL Server}'


# Connect to the database
def create_connection():
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(connection_string)
    return conn


# Create the YouTubeVotes table
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        IF OBJECT_ID('dbo.YoutTubeVotes', 'U') IS NOT NULL
        DROP TABLE dbo.YoutTubeVotes;

        CREATE TABLE dbo.YoutTubeVotes (
            UserName NVARCHAR(255),
            Comment NVARCHAR(MAX),
            VotedFor NVARCHAR(255)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


# List of names with corresponding vote counts
word_list = {
    'MODE YULE G': 0,
    'MITCHY THE RAPPER': 0,
    'DECO': 0,
    'SLINGER TRIPPLE ONE': 0,
    'ACID FLAMES': 0,
    'ORIGNAL STINGER': 0,
    'PENDA PENDA MUSIC': 0
}


def get_comments(video_id):
    comments = []
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    ).execute()

    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append((author, comment))
        if 'nextPageToken' in response:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100,
                textFormat="plainText"
            ).execute()
        else:
            break
    return comments


def process_comments(comments, word_list):
    conn = create_connection()
    cursor = conn.cursor()

    for author, comment in comments:
        print(f"Comment: {comment}")  # Print each comment
        voted_for = None
        comment_upper = comment.upper()
        for full_name in word_list.keys():
            name_parts = [part.upper() for part in full_name.split() if len(part) > 3]  # Split and filter parts

            # Check if the comment starts with any part of the name
            if any(comment_upper.startswith(part) for part in name_parts):
                word_list[full_name] += 1
                voted_for = full_name
                break  # Move to the next comment after counting for this name

        cursor.execute('''
            INSERT INTO dbo.YoutTubeVotes (UserName, Comment, VotedFor)
            VALUES (?, ?, ?)
        ''', (author, comment, voted_for))

    conn.commit()
    cursor.close()
    conn.close()


def main(video_url):
    # Extract video ID from the URL
    video_id = video_url.split("v=")[-1]

    # Create the table
    create_table()

    # Fetch the comments from the video
    comments = get_comments(video_id)

    # Process the comments to count votes and store in the database
    process_comments(comments, word_list)

    # Display the final vote count
    for word, count in word_list.items():
        print(f"{word}: {count}")


# Example usage
video_url = 'https://www.youtube.com/watch?v=hnqa7RG4vBo'  # Replace with the actual video URL
main(video_url)
