import tkinter as tk
import wikipedia
from nltk.corpus import stopwords
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
import re

sentTokens = []
wordTokens = []
lemTokens = []
summerisedInfo = ''

def get_part_of_speech_tags(token):
     tag_dict = {"J": wordnet.ADJ,
                 "N": wordnet.NOUN,
                 "V": wordnet.VERB,
                 "R": wordnet.ADV}

     tag = nltk.pos_tag([token])[0][1][0].upper() 
     return tag_dict.get(tag, wordnet.NOUN)

def vectoriseAndSave():
    global lemTokens
    vectorizer = CountVectorizer()
    vectorizer.fit(lemTokens)
    writeToFile("VectorizedWords.txt", "Vectorized Words: \n" + str(vectorizer.vocabulary_))

def writeToFile(path, contents):
    file = open(path, "w")
    file.write(contents)
    file.close()

def close_window(root):
        root.destroy()

def lemmitiseAndSave():
    global lemTokens
    global wordTokens
    lemmatizer = WordNetLemmatizer()

    for token in wordTokens:
        lemmatisedtoken = lemmatizer.lemmatize(token, get_part_of_speech_tags(token))
        lemTokens.append(lemmatisedtoken)
    writeToFile('LemmitisedTokens.txt','Lemmitised Tokens: \n' + str(lemTokens))

def showInfo(txt1, txt2):
    root = tk.Tk()
    root.title("Grand Prix Summary")

    label1 = tk.Label(root, text=txt1, wraplength=700)
    label1.pack(pady=10)

    label2 = tk.Label(root, text=txt2 , wraplength=700)
    label2.pack(pady=10)

    button = tk.Button(root, text="OK", command=lambda: close_window(root))
    button.pack(pady=10)

    root.update_idletasks()
    root.minsize(root.winfo_width(), root.winfo_height())

    root.mainloop()

def getSentimentScore(text):
    sa=SentimentIntensityAnalyzer()
    sentimentScore = sa.polarity_scores(text)
    score = sentimentScore['compound']
    whatToReturn = ""
    if score < 0:
        whatToReturn = "negative"
    elif score > 0:
        whatToReturn = "positive"
    else:
        whatToReturn = "neutral"
    return whatToReturn

def summerise():
    freqTable = dict()
    for word in wordTokens:
        word = word.lower()
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1
        
    sentenceValue = dict()

    for sentence in sentTokens:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if word in sentence.lower():
                    if sentence in sentenceValue:
                        sentenceValue[sentence] += freq
                    else:
                        sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    average = int(sumValues / len(sentenceValue))
    summary = ''

    for sentence in sentTokens:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence
    return summary
    
def getInfoSubject(infoTocheck):
    freq = nltk.FreqDist(wordTokeniseAndClean(infoTocheck))
    subject = ""
    subjectFreq = 0
    for key,val in freq.items():
        if int(val) > subjectFreq:
            subjectFreq = int(val)
            subject = str(key)
    return subject.lower()


def getInfoFromWiki(country, years):
    global root
    global summerisedInfo
    info = ""
    cont = False
    for year in years:
        page = wikipedia.page(str(year)+ '_' + country + '_Grand_Prix')
        if (getInfoSubject(page.summary) in (year, str(country).lower(), 'grand', 'prix', 'formula', '1', 'one', 'race', 'event')):
            info += page.summary + ' '
            cont = True
        else:
            input(getInfoSubject(page.summary))
    if (cont):
        root.destroy()
        setTokenArrays(info)
        summerisedInfo = summerise()
        showInfo(summerisedInfo, 'This text is '+ str(getSentimentScore(summerisedInfo) + '.'))
        # print (summerisedInfo)
        # print ('The sentiment score for this text is '+ str(getSentimentScore(summerisedInfo)))
        writeToFile("info.txt", re.sub('[^A-Za-z0-9 ]+', '', info))
        writeToFile("Summerised Info.txt", summerisedInfo)
    

def wordTokeniseAndClean(text):
    tokens = text.split()
    cleanTokens = tokens[:]
    for token in tokens:
        if token.lower() in stopwords.words('english'):
            cleanTokens.remove(token)
    return cleanTokens[:]

def setTokenArrays(text):
    global wordTokens
    global sentTokens
    wordTokens = wordTokeniseAndClean(text)
    sentTokens = nltk.sent_tokenize(text)
    writeToFile('WordTokens.txt', 'Word Tokens: \n' + str(wordTokens))
    writeToFile('SentTokens.txt', 'Sentence Tokens: \n' + str(sentTokens))
    lemmitiseAndSave()
    vectoriseAndSave()
    

def submit_form():
    country = country_entry.get()
    years = []
    years.append(year1_entry.get())
    years.append(year2_entry.get())
    years.append(year3_entry.get())
    print(f"Country: {country}, Year 1: {years[0]}, Year 2: {years[1]}, Year 3: {years[2]}")
    getInfoFromWiki(country, years)
    
    

root = tk.Tk()
root.title("Grand Prix Summery")

# Create a frame for the input fields
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10)

# Create the Country Name input field
country_label = tk.Label(input_frame, text="Country Name:")
country_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
country_entry = tk.Entry(input_frame)
country_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Create the Year 1 input field
year1_label = tk.Label(input_frame, text="Year 1:")
year1_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
year1_entry = tk.Entry(input_frame)
year1_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Create the Year 2 input field
year2_label = tk.Label(input_frame, text="Year 2:")
year2_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
year2_entry = tk.Entry(input_frame)
year2_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Create the Year 3 input field
year3_label = tk.Label(input_frame, text="Year 3:")
year3_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
year3_entry = tk.Entry(input_frame)
year3_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Create the Submit button
submit_button = tk.Button(root, text="Submit", command=submit_form)
submit_button.pack(padx=10, pady=10)

root.mainloop()
