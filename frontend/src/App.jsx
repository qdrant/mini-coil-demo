import { useCallback, useEffect, useState } from 'react';
import './App.css';
import logo from './assets/logo.svg';
import { queryEmbeddings } from './queries';
import Visualization from './components/Visualization.jsx';
import SentenceInput from './components/SentenceInput.jsx';
import SentencesView from './components/SentencesView.jsx';

function App() {
  const [sentenceList, setSentenceList] = useState([]);
  const [selectedWord, setSelectedWord] = useState(null);
  const [selectedWords, setSelectedWords] = useState([]);

  useEffect(() => {
    // request to the server
    // console.log(sentenceList);
  }, [sentenceList]);

  const getSentence = (sentenceObj) => {
    return Object.keys(sentenceObj)[0];
  }

  const getSentenceWords = (sentenceObj) => {
    return Object.values(sentenceObj)[0];
  }

  const handleSentenceInput = async (s) => {
    let sentences = s.split('\n');
    let newEntries = [];

    for (let i = 0; i < sentences.length; i++) {
      let sentence = sentences[i];
      if (sentence.trim() === '') {
        continue;
      }
      const embeddings = await queryEmbeddings(sentence);
      const newEntry = { [sentence]: embeddings };
      newEntries.push(newEntry);

    }

    setSentenceList([...sentenceList, ...newEntries]);
  };

  const selectWordObjects = (selectedWord) => {
    let selectedWordObj = [];
    for (let i = 0; i < sentenceList.length; i++) {
      let sentence = getSentence(sentenceList[i]);
      let sentenceWords = getSentenceWords(sentenceList[i]);
      let words = Object.values(sentenceWords);
      for (let j = 0; j < words.length; j++) {
        let wordObj = words[j];
        if (wordObj.word === selectedWord) {
          selectedWordObj.push({
            sentence: sentence,
            ...wordObj,
          });
        }
      }
    }
    return selectedWordObj;
  }


  const handleWordClick = (wordObj) => {
    setSelectedWord(wordObj.word);
  }

  const wrappedWords = useCallback(() => {

  }, [sentenceList, selectedWord]);


  useEffect(() => {
    const hasSelectedWord = selectedWord !== null;
    let currentSelectedWords = [];

    if (hasSelectedWord) {
      currentSelectedWords = selectWordObjects(selectedWord);
    }

    setSelectedWords(currentSelectedWords);
  }, [selectedWord, sentenceList]);

  return (
    <div className="w-100 h-[100vh] max-h-[100vh]">
      <div className="flex flex-col gap-y-4 mt-4 mb-2.5 w-100 lg:w-[60vw] px-6 mx-auto">
        <div className="flex justify-center mb-10">
          <img src={logo} className="h-9" alt="Qdrant logo" />
        </div>
        <section className="
          max-h-[30vh]
          overflow-y-auto
          ">
          <SentencesView
            sentenceList={sentenceList}
            selectedWord={selectedWord}
            handleWordClick={handleWordClick}
            removeSentence={(index) => { setSentenceList(sentenceList.filter((_, i) => i !== index)); }}
          />
          <div className="flex gap-2 relative">
            <SentenceInput addSentence={handleSentenceInput} />
          </div>
        </section>

        <section className="
          h-[50vh]
          pb-5
          ">
          {selectedWords.length > 0 && <Visualization selectedWords={selectedWords} word={selectedWord} />}
        </section>
      </div>
    </div>
  );
}

export default App;
