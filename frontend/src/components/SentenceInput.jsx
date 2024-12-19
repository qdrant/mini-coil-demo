import PropTypes from 'prop-types';
import { useRef, useState } from 'react';

const SentenceInput = ({ addSentence }) => {

    const textareaRef = useRef();
    const [loading, setLoading] = useState(false);
    const [sentence, setSentence] = useState(``.trim());

    const textInputHeight = "42px";


    const handleAddSentence = async () => {
        setLoading(true);

        let _result = await addSentence(sentence);

        setLoading(false);
        setSentence('');

        textareaRef.current.style.height = textInputHeight;
        textareaRef.current.focus();
    };


    return <>
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
                    handleAddSentence()
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
                handleAddSentence()
                    .catch((err) => {
                        console.error(err);
                    });
            }}
        >
            ✓
        </button>

    </>


}

SentenceInput.propTypes = {
    addSentence: PropTypes.func.isRequired,
};

export default SentenceInput;

