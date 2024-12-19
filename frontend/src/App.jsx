import { useEffect, useState } from 'react';
import './App.css';
import logo from './assets/logo.svg';
import { queryEmbeddings } from './queries';
import Visualization from './components/Visualization.jsx';
import VisualizationGraph from './components/VisualizationGraph.jsx';
import SentenceInput from './components/SentenceInput.jsx';
import SentencesView from './components/SentencesView.jsx';
import ExampleSelector from './components/ExampleSelector.jsx';

function App() {
  const [sentenceList, setSentenceList] = useState([]);
  const [selectedWord, setSelectedWord] = useState(null);
  const [selectedWords, setSelectedWords] = useState([]);
  const [useGraph, setUseGraph] = useState(false);

  const getSentence = (sentenceObj) => {
    return Object.keys(sentenceObj)[0];
  }

  const getSentenceWords = (sentenceObj) => {
    return Object.values(sentenceObj)[0];
  }

  const prepareSentence = async (s) => {
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

    return newEntries;
  }

  const handleSentenceInput = async (s) => {
    let newEntries = await prepareSentence(s);
    setSentenceList([...sentenceList, ...newEntries]);
  };

  const overwriteSentenceInput = async (s) => {
    let newEntries = await prepareSentence(s);
    setSentenceList(newEntries);
  }

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
          break;
        }
      }
    }
    return selectedWordObj;
  }


  const handleWordClick = (wordObj) => {
    setSelectedWord(wordObj.word);
  }

  useEffect(() => {
    const hasSelectedWord = selectedWord !== null;
    let currentSelectedWords = [];

    if (hasSelectedWord) {
      currentSelectedWords = selectWordObjects(selectedWord);
    }

    console.log("currentSelectedWords", currentSelectedWords);

    setSelectedWords(currentSelectedWords);
  }, [selectedWord, sentenceList]);


  return <div className="container m-auto grid grid-cols-4 gap-1 text-white md:grid-cols-12">
    <header className="col-span-full bg-slate-600 p-4">
      <div className="flex justify-center mb-10">
        <img src={logo} className="h-9" alt="Qdrant logo" />
      </div>
    </header>
    <main className="col-span-4 bg-slate-600 p-4 md:col-span-7">
      <div className="flex gap-2 relative">
        <SentenceInput addSentence={handleSentenceInput} />
      </div>

      <ExampleSelector addSentence={(sentence) => { overwriteSentenceInput(sentence) }} />

      <SentencesView
        sentenceList={sentenceList}
        selectedWord={selectedWord}
        handleWordClick={handleWordClick}
        removeSentence={(index) => { setSentenceList(sentenceList.filter((_, i) => i !== index)); }}
      />

    </main>
    <aside className="col-span-5 bg-slate-600 p-4 gap-2">
      {
        // Toggle between Visualization and VisualizationGraph components
        // Aligned to the right of the screen
      }
      <div className="flex justify-end gap-2">
        <button
          className={`btn p-2 border ${useGraph ? "border-neutral-50" : "border-secondary-violet-50"} rounded text-neutral-90`}
          onClick={() => setUseGraph(false)}
        >Scatter</button>
        <button
          className={`btn p-2 border ${!useGraph ? "border-neutral-50" : "border-secondary-violet-50"} rounded text-neutral-90`}
          onClick={() => setUseGraph(true)}
        >Graph</button>
      </div>

      <div className='h-[50vh]'>
        {
          useGraph ?
            <VisualizationGraph selectedWords={selectedWords} word={selectedWord} /> :
            <Visualization selectedWords={selectedWords} word={selectedWord} />
        }
      </div>
    </aside>
  </div>;
}

export default App;
