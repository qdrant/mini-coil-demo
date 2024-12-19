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
        "An example of a viral vector vaccine is the rVSV-ZEBOV vaccine against Ebola.",
        "Whether you are an illustrator, designer, web designer or just someone who needs to create some vector imagery, Inkscape is for you!",
        "Qdrant is an Open-Source Vector Database and Vector Search Engine written in Rust. It provides fast and scalable vector similarity search service",
        "Free Vectors and Icons in SVG format. Download free mono or multi color vectors for commercial use.",
        "Other viral vector-based COVID-19 vaccines have also undergone extensive preclinical evaluations, including vesicular stomatitis virus",
        "For high-dimensional data, tree-based exact vector search techniques such as the k-d tree and R-tree do not perform well enough because of the curse of dimensionality."
    ],
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