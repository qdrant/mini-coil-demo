import { useCallback, useEffect, useImperativeHandle, useRef, useState } from 'react';
import './App.css';
import logo from './assets/logo.svg';
import { queryEmbeddings } from './queries';
import Visualization from './components/Visualization.jsx';
import { colors } from './common/colors.js';

function App() {
  const textareaRef = useRef();
  const [sentence, setSentence] = useState(`
Unknown Vector provides its users with digital media add-ons that simplify online video discovery, sharing, publishing, and organizing.
VECTOR is an European provider of solutions for a rapidly developing telecommunications industry.
GL Stock Images is a marketplace for royalty-free stock photos and vector illustrations.
Designious is a design studio that creates great vector illustrations and design elements.
Vector City Racers is an online gaming site.
`.trim());
  const [sentenceList, setSentenceList] = useState([]);
  const [selectedWord, setSelectedWord] = useState(null);
  const [selectedWords, setSelectedWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const textInputHeight = '82px';

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

  const tokenizeSentence = (sentence) => {
    let regex = /\b/;
    return sentence.split(regex);
  }

  const handleSentenceInput = async (s) => {
    setLoading(true);

    let sentences = s.split('\n');
    let newEntries = [];

    for (let i = 0; i < sentences.length; i++) {
      let sentence = sentences[i];
      if (sentence.trim() === '') {
        continue;
      }
      const embeddings = await queryEmbeddings(sentence);
      const newEntry = {[sentence]: embeddings};
      newEntries.push(newEntry);
      
    }
    
    setSentenceList([...sentenceList, ...newEntries]);
    setSentence('');
    setLoading(false);
    textareaRef.current.style.height = textInputHeight;
    textareaRef.current.focus();
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
    return sentenceList.map((sentenceObj, index) => {
      const sentence = getSentence(sentenceObj);
      return (
        <li key={index} className="list-none mb-7 flex justify-between">
          <span>
            {tokenizeSentence(sentence)
              .map((word, i) => {

                let wordLower = word.toLowerCase();
                
                let wordParsed = hasOwnProperty.call(sentenceObj[sentence], wordLower);
                let sentenceWord = sentenceObj[sentence][wordLower];
                let isVocab = wordParsed && sentenceWord.word_id !== -1;

                if (!wordParsed || !isVocab) {
                  return (
                    <span
                      key={i}
                      className={`
                      inline-block
                      text-neutral-80
                      cursor-default
                      mr-1
                      mb-0.5
                      `}
                    >
                      {word}
                    </span>
                  );
                } else {
                  const wordObj = {[word]: {...sentenceWord}};
                  
                  const colorId = sentenceWord.word_id % 12;
                  const colorName = "color" + colorId;
                  const colorPalette = colors[colorName];
                  const isSelected = selectedWord === wordObj[word].word;

                  return (
                    <span
                      key={i}
                      className={`
                      inline-block
                      text-neutral-100
                      cursor-pointer
                      ${isSelected ? 'font-bold underline' : ''}
                      mr-1
                      mb-0.5
                      word-hover
                      `}
                      style={{
                        backgroundColor: colorPalette[30],
                        "--word-hover": colorPalette[50],
                      }}
                      onClick={() => handleWordClick({
                        ...sentenceWord,
                        sentence: sentence,
                      })}
                    >
                      {word}
                    </span>
                  );
                }

              })}
          </span>
          <button
            className="text-neutral-80 cursor-pointer"
            onClick={() => {
              setSentenceList(sentenceList.filter((_, i) => i !== index));
            }}
          >
            x
          </button>
        </li>
      );
    });
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
          {sentenceList?.length ? <ul>{wrappedWords()}</ul> : <></>}
          <div className="flex gap-2 relative">
            <textarea
              ref={textareaRef}
              rows={1}
              maxLength={280}
              className={`
              h-auto
              overflow-hidden
              max-h-[30vh]
              w-full
              text-neutral-98
              text-[transparent]
              caret-neutral-98
              placeholder:text-neutral-80
              px-3
              py-2
              border
              border-neutral-50
              rounded
              bg-neutral-10
              bg-[linear-gradient(45deg,transparent_25%,rgba(22,30,51,0.7)_50%,transparent_75%,transparent_100%)]
              bg-[length:250%_250%,100%_100%]
              bg-[position:-100%_0,0_0]
              bg-no-repeat
              focus:outline-none
              focus:border-neutral-98
              ${loading ? 'animate-shine' : ''} 
              `}
              placeholder="Type your text here..."
              value={sentence}
              onChange={(e) => {
                // resize textarea based on content
                textareaRef.current.style.height = "auto";
                textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';

                setSentence(e.target.value);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleSentenceInput(sentence)
                  .catch((err) => {
                    console.error(err);
                  });
                }
              }}
            />
            {loading && (
              <div className="flex gap-1 justify-center items-center absolute right-16 top-0 bottom-0">
                <span className="sr-only">Loading...</span>
                <div className="h-1 w-1 bg-secondary-violet-90 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="h-1 w-1 bg-secondary-violet-90 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="h-1 w-1 bg-secondary-violet-70 rounded-full animate-bounce"></div>
              </div>
            )}
            <button
              className="h-full
              px-3
              py-2
              border
              border-neutral-50
              rounded
              text-neutral-90
              hover:text-neutral-98
              hover:border-neutral-30
              hover:bg-neutral-30
              cursor-pointer"
              title="Add an inpit"
              disabled={!sentence.trim()}
              onClick={() => {
                handleSentenceInput(sentence)
                  .catch((err) => {
                    console.error(err);
                  });
              }}
            >
              ✓
            </button>
          </div>
          </section>

          <section className="
          h-[50vh]
          pb-5
          ">
          { selectedWords.length > 0 && <Visualization selectedWords={selectedWords} word={selectedWord} /> }
          </section>
        </div>
      </div>
  );
}

export default App;
