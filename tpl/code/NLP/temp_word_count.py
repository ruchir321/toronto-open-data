
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import re
from collections import Counter

def clean_text(text):
    """
    Cleans the text by removing HTML tags, punctuation, and converting to lowercase.
    """
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove punctuation and special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    return text

def get_word_counts():
    """
    Calculates and prints the most common words in the event descriptions.
    """
    # Read the cleaned events data
    try:
        df = pd.read_csv("data/cleaned_events.csv")
    except FileNotFoundError:
        print("Error: data/cleaned_events.csv not found. Please run the data cleaning script first.")
        return

    # Clean the description column
    df['cleaned_description'] = df['description'].apply(clean_text)

    # Combine all descriptions into a single string
    text = " ".join(df['cleaned_description'])

    # Add custom stopwords
    stopwords = set(STOPWORDS)
    custom_stopwords = ['br', 'program', 'library', 'registration', 'required', 'register', 'please', 'call', 'email', 'visit', 'information', 'join', 'toronto', 'public', 'free', 'event', 'learn', 'new', 'workshop', 'series', 'class', 'sessions', 'session', 'participants', 'participant', 'adults', 'children', 'kids', 'teens', 'family', 'families', 'ages', 'old', 'years', 'year', 'month', 'monthly', 'weekly', 'week', 'day', 'days', 'time', 'times', 'date', 'dates', 'pm', 'am', 'room', 'space', 'limited', 'drop', 'person', 'phone', 'email', 'website', 'online', 'link', 'http', 'https', 'www', 'com', 'ca', 'org', 'net', 'gov', 'edu', 'info', 'biz', 'name', 'title', 'description', 'eventbrite', 'zoom', 'google', 'microsoft', 'apple', 'android', 'ios', 'windows', 'mac', 'linux', 'pc', 'computer', 'laptop', 'tablet', 'phone', 'device', 'app', 'software', 'hardware', 'internet', 'web', 'website', 'browser', 'search', 'online', 'digital', 'virtual', 'live', 'stream', 'video', 'audio', 'image', 'photo', 'picture', 'file', 'document', 'pdf', 'word', 'excel', 'powerpoint', 'gmail', 'outlook', 'hotmail', 'yahoo', 'mail', 'message', 'text', 'chat', 'call', 'voicemail', 'fax', 'address', 'location', 'city', 'province', 'country', 'postal', 'code', 'zip', 'street', 'road', 'avenue', 'boulevard', 'drive', 'lane', 'court', 'place', 'square', 'park', 'building', 'floor', 'room', 'suite', 'unit', 'apartment', 'condo', 'house', 'home', 'office', 'school', 'university', 'college', 'institute', 'academy', 'center', 'centre', 'club', 'group', 'team', 'organization', 'company', 'business', 'store', 'shop', 'restaurant', 'cafe', 'bar', 'hotel', 'motel', 'hospital', 'clinic', 'doctor', 'nurse', 'patient', 'medicine', 'health', 'wellness', 'fitness', 'sport', 'game', 'music', 'song', 'dance', 'art', 'craft', 'hobby', 'book', 'read', 'write', 'author', 'poet', 'story', 'poem', 'novel', 'magazine', 'newspaper', 'journal', 'blog', 'post', 'article', 'news', 'report', 'paper', 'letter', 'note', 'card', 'ticket', 'pass', 'key', 'lock', 'door', 'window', 'wall', 'floor', 'ceiling', 'roof', 'stair', 'elevator', 'car', 'bus', 'train', 'subway', 'metro', 'tram', 'trolley', 'bike', 'motorcycle', 'scooter', 'boat', 'ship', 'plane', 'airport', 'station', 'stop', 'terminal', 'gate', 'platform', 'track', 'road', 'street', 'highway', 'freeway', 'bridge', 'tunnel', 'park', 'garden', 'forest', 'mountain', 'hill', 'valley', 'river', 'lake', 'ocean', 'sea', 'beach', 'island', 'peninsula', 'continent', 'country', 'state', 'province', 'city', 'town', 'village', 'neighborhood', 'district', 'zone', 'area', 'region', 'world', 'universe', 'galaxy', 'star', 'planet', 'moon', 'sun', 'sky', 'cloud', 'rain', 'snow', 'wind', 'storm', 'weather', 'climate', 'temperature', 'degree', 'celsius', 'fahrenheit', 'kelvin', 'meter', 'kilometer', 'mile', 'yard', 'foot', 'inch', 'centimeter', 'millimeter', 'liter', 'milliliter', 'gallon', 'quart', 'pint', 'cup', 'ounce', 'pound', 'kilogram', 'gram', 'ton', 'hour', 'minute', 'second', 'day', 'week', 'month', 'year', 'decade', 'century', 'millennium', 'morning', 'afternoon', 'evening', 'night', 'midnight', 'noon', 'sunrise', 'sunset', 'dawn', 'dusk', 'today', 'tomorrow', 'yesterday', 'now', 'then', 'soon', 'late', 'early', 'always', 'never', 'sometimes', 'often', 'usually', 'rarely', 'seldom', 'ever', 'not', 'no', 'yes', 'ok', 'sure', 'please', 'thank', 'you', 'me', 'my', 'mine', 'i', 'we', 'us', 'our', 'ours', 'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them', 'their', 'theirs', 'who', 'whom', 'whose', 'which', 'what', 'where', 'when', 'why', 'how', 'a', 'an', 'the', 'and', 'but', 'or', 'so', 'if', 'then', 'else', 'while', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']
    stopwords.update(custom_stopwords)

    # Tokenize the text
    words = text.split()

    # Remove stopwords from the word list
    words = [word for word in words if word not in stopwords]

    # Count word frequencies
    word_counts = Counter(words)

    # Print the 10 most common words
    print("Top 10 most common words:")
    for word, count in word_counts.most_common(10):
        print(f"{word}: {count}")

if __name__ == '__main__':
    get_word_counts()
