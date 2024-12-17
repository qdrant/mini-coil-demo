import { useCallback, useEffect, useRef, useState } from 'react';
import './App.css';
import logo from './assets/logo.svg';
import { queryEmbeddings } from './queries';
import Visualization from './components/Visualization.jsx';

function App() {
  const textareaRef = useRef();
  const [sentence, setSentence] = useState('');
  const [sentenceList, setSentenceList] = useState([]);
  const [loading, setLoading] = useState(false);
  const textInputHeight = '42px';

  useEffect(() => {
    // request to the server
    console.log(sentenceList);
  }, [sentenceList]);

  const getSentence = (sentenceObj) => {
    return Object.keys(sentenceObj)[0];
  }

  const handleSentenceInput = async (s) => {
    setLoading(true);
    const embeddings = await queryEmbeddings(s);
    const newEntry = {[s]: embeddings};
    setSentenceList([...sentenceList, newEntry]);
    setSentence('');
    setLoading(false);
    textareaRef.current.style.height = textInputHeight;
    textareaRef.current.focus();
  };

  const handleWordClick = (wordObj) => {
    console.log(wordObj);
  }

  const wrappedWords = useCallback(() => {
    return sentenceList.map((sentenceObj, index) => {
      const sentence = getSentence(sentenceObj);
      return (
        <li key={index} className="list-none mb-2 flex justify-between">
          <span>
            {sentence
              .trim()
              .split(' ')
              .map((word, i) => {
                const wordObj = {[word]: {...sentenceObj[sentence][word]}};
                return (
                  <span
                    key={i}
                    className="
                    inline-block
                    text-secondary-violet-90
                    bg-secondary-violet-30
                    hover:bg-secondary-violet-50
                    hover:text-secondary-violet-90
                    cursor-pointer
                    mr-1
                    mb-0.5
                    "
                    onClick={() => handleWordClick(wordObj)}
                  >
                    {word}
                  </span>
                );
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
  }, [sentenceList]);

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
              className={`
              h-[${textInputHeight}]
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
                textareaRef.current.style.height = textInputHeight;
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
          <Visualization sentence={sentence} />
          </section>
        </div>
      </div>
  );
}

export default App;
