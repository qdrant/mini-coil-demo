import PropTypes from 'prop-types';


const examples = {
    "bat": [
        "The delicate skeletons of bats do not fossilise well; it is estimated that only 12% of bat genera that lived have been found in the fossil record.",
        "Owls, hawks and snakes eat bats, but that’s nothing compared to the millions of bats dying from white-nose syndrome.",
        "Bats account for more than a quarter of mammal species in the UK and around 20% of all mammal species worldwide.",
        "Coach Pitch/Junior Big Barrel bats are typically for ages 7-8 and feature a larger barrel and light swing weight to provide the player with a greater chance to make solid contact.",
        "The Marucci CAT X Composite BBCOR bat is the perfect choice for serious players who want to take their game to the next level.",
        "Send hits flying like lighting with an electric Neon Yellow version of baseball’s most dominant two-piece hybrid BBCOR bat featuring a heavy-hitting X14 Alloy Barrel.",
    ],
    "vector": [
        "vector search",
        "vector index",
        "vector space",
        "vector image",
        "vector graphics",
        "vector illustration",
    ],
    "watch": [
        "I always wear a silver watch to keep track of time.",
        "Let’s watch the sunset together from the balcony.",
        "He subscribed to the new streaming service to watch his favorite shows.",
        "The mountain climber was careful to watch her footing on the icy trail.",
        "She glanced at her watch and realized she was running late for the meeting.",
        "His collection includes a rare Swiss watch made in the early 1900s.",
    ]
}


const ExampleSelector = ({ useExample }) => {
    const handleExampleClick = (word, sentences) => {
        useExample(word, sentences);
    }

    let buttons = [];

    for (let [word, sentences] of Object.entries(examples)) {

        let joinedSentences = sentences.join('\n');

        buttons.push(
            <button 
                key={word}
                className="btn pt-1 pb-1 pl-2 pr-2 border border-neutral-50 rounded text-neutral-90 mt-4 ml-2"
                onClick={() => handleExampleClick(word, joinedSentences)}
            >
                {word}
            </button>
        );
    }

    return (<div>
        <span className="text-neutral-90">Examples:</span> 
        {buttons}
    </div>);
}

ExampleSelector.propTypes = {
    useExample: PropTypes.func.isRequired,
};

export default ExampleSelector;