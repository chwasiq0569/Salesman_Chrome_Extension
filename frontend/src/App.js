/* global chrome */
import React from 'react';
import './App.css';
import ScrapeLoader from "./assets/waiting.gif"
import SiteLogo from "./assets/logo.PNG"
import PuffLoader from "react-spinners/PuffLoader";
import { PieChart } from 'react-minimal-pie-chart';

function App() {
  const [currentUrl, setCurrentUrl] = React.useState('');
  const [userInput, setUserInput] = React.useState("");
  const [loading, setLoading] = React.useState(0)
  const [websiteContent, setWebsiteContent] = React.useState("");
  const [geminiResponse, setGeminiResponse] = React.useState("");
  const [reviewsSentiments, setReviewsSentiments] = React.useState("");
  const [displayChat, setDisplayChat] = React.useState(true);
  const [positive_reviews, setPositiveReviews] = React.useState([]);
  const [negative_reviews, setNegativeReviews] = React.useState([]);
  const [neutral_reviews, setNeutralReviews] = React.useState([]);
  const [reviews_loading, setReviewsLoading] = React.useState(true)

  var pos_values = [];
  var neu_values = [];
  var neg_values = [];
  const format_reviews = (originalArray) => {
    console.log('originalArray', originalArray)
    originalArray.forEach(item => {
      for (let key in item) {
        if (key === "roberta_pos") {
          pos_values.push(item[key]);
        } else if (key === "roberta_neu") {
          neu_values.push(item[key]);
        } else if (key === "roberta_neg") {
          neg_values.push(item[key]);
        }
      }
    });

    console.log('pos_values', pos_values);
    console.log('neu_values', neu_values);
    console.log('neg_values', neg_values);

    setPositiveReviews(pos_values)
    setNegativeReviews(neg_values)
    setNeutralReviews(neu_values)
    setReviewsLoading(false)
  }

  const [conversationArray, setConversationArray] = React.useState([
    {
      "Bot": "Hi How can I help you?"
    }
  ]);

  const scrapeSite = (link) => {
    setLoading(1)
    fetch(process.env.SCRAPE_SITE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        link: link
      }),
    })
      .then(response => response.json())
      .then(data => {
        setLoading(0)
        console.log(data)
        setWebsiteContent(data.context)
        sentimentAnalysis(data.context)
      })
      .catch(error => console.error(error));
  }

  const findAnswer = (websiteContent, question) => {
    setLoading(3)
    fetch(process.env.GET_ANSWER, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        context: websiteContent,
        question: question
      }),
    })
      .then(response => response.json())
      .then(data => {
        setLoading(0)
        console.log(data)
        setGeminiResponse(data)
        setConversationArray((prev) => [...prev, { "Bot": data.result }])
      })
      .catch(error => console.error(error));
  }

  const sentimentAnalysis = (context) => {
    setLoading(2)
    fetch(process.env.GET_SENTIMENT_ANALYSIS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        context: context
      }),
    })
      .then(response => response.json())
      .then(data => {
        setLoading(0)
        console.log(data)
        setReviewsSentiments(data)
        format_reviews(data.reviews)
      })
      .catch(error => console.error(error));
  }

  React.useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].url) {
        setCurrentUrl(tabs[0].url);
        scrapeSite(tabs[0].url)
      }
    });
  }, []);

  return (
    <div>
      <div className='header'>
        <img className='logo' src={SiteLogo} alt="logo" />{!reviews_loading && <p onClick={() => setDisplayChat(!displayChat)}>{displayChat ? "Reviews" : "Chat"}</p>}
      </div>
      {
        loading == 1 && <div className="splashScreen"><img src={ScrapeLoader} alt="loading_screen" /></div>
      }
      {
        displayChat ? <>
          <div className='messages-container'>
            {
              conversationArray.map((convo, index) => (
                <div className='user-message' key={index}>
                  <p style={{ fontWeight: "500" }}>{Object.keys(convo)[0]}</p>: <p>{convo[Object.keys(convo)[0]]}</p>
                </div>
              ))
            }
          </div>
          <div className='userInput'>
            <input onChange={(e) => setUserInput(e.target.value)} type='text' value={userInput} placeholder='Type Something...' />
            {
              loading == 3 ? <PuffLoader color="#36d7b7" /> : <button onClick={() => {
                setConversationArray((prev) => [...prev, { "You": userInput }])
                setUserInput("")
                console.log(websiteContent)
                websiteContent && findAnswer(websiteContent, userInput)
              }}>Ask</button>
            }
          </div>
        </> : <div className='pie-chart-container'>
          <div className='chat-container'>
            <p className='sentimentAnalysisText'>Sentiment Analysis on People's Reviews</p>
            <PieChart animate={true}
              data={[
                { title: 'Positive', value: positive_reviews.length, color: '#FFFFFF' },
                { title: 'Negative', value: negative_reviews.length, color: '#000000' },
                { title: 'Neutral', value: neutral_reviews.length, color: '#FFFF00' },
              ]}
              label={({ dataEntry }) => dataEntry.title}
              labelStyle={{
                fill: '#2EC26A',
                fontSize: '6px',
                fontFamily: 'Poppins, sans-serif'
              }}
            /></div>
        </div>
      }
    </div>
  );
}

export default App;
