import PropTypes from 'prop-types';
import { useState } from 'react';


const getSentence = (sentenceObj) => {
    return Object.keys(sentenceObj)[0];
}

const tokenizeSentence = (sentence) => {
    let regex = /\b/;
    return sentence.split(regex);
}

function regularSpan(i, word) {
    return (<span
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
    </span>);
}

function highlightableSpan(i, word, isSelected, isHighlighted, onClick, onHover, onLeave) {
    return (
        <span
            key={i}
            className={`
          inline-block
          text-neutral-100
          cursor-pointer
          ${isHighlighted ? 'underline' : ''}
          ${isSelected ? 'bg-secondary-violet-50 hover:bg-secondary-violet-30' : 'bg-neutral-30 hover:bg-neutral-20'}
          mr-1
          mb-0.5
          `}
            onClick={onClick}
            onMouseEnter={onHover}
            onMouseLeave={onLeave}
        >
            {word}
        </span>
    );
}


function generateList(sentenceList, selectedWord, hoveredWord, handleWordClick, handleWordHover, removeSentence) {
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
                                return regularSpan(i, word);
                            } else {
                                const wordObj = { [word]: { ...sentenceWord } };

                                const isSelected = selectedWord === wordObj[word].word;
                                const isHighlighted = hoveredWord === wordObj[word].word;

                                const onClick = () => handleWordClick({
                                    ...sentenceWord,
                                    sentence: sentence,
                                });

                                const onHover = () => handleWordHover(wordObj[word].word);
                                const onLeave = () => handleWordHover(null);

                                return highlightableSpan(i, word, isSelected, isHighlighted, onClick, onHover, onLeave);
                            }

                        })}
                </span>
                <button
                    className="text-neutral-80 cursor-pointer"
                    onClick={() => {
                        removeSentence(index);
                        // setSentenceList(sentenceList.filter((_, i) => i !== index));
                    }}
                >
                    x
                </button>
            </li>
        );
    });
}


const SentencesView = ({ sentenceList, selectedWord, handleWordClick, removeSentence }) => {
    const [wordHover, setWordHover] = useState(null);


    return sentenceList?.length ? <ul>{generateList(
        sentenceList,
        selectedWord,
        wordHover,
        handleWordClick,
        setWordHover,
        removeSentence
    )}</ul> : <></>
}



SentencesView.propTypes = {
    sentenceList: PropTypes.array.isRequired,
    selectedWord: PropTypes.string,
    handleWordClick: PropTypes.func.isRequired,
    removeSentence: PropTypes.func.isRequired,
};

export default SentencesView;

