import PropTypes from 'prop-types';
import { useEffect, useRef } from 'react';
import ForceGraph from 'force-graph';


const cosineSimilarity = (a, b) => {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

const VisualizationGraph = ({ selectedWords, word }) => {
    const graphRef = useRef(null);

    useEffect(() => {
        const elem = document.getElementById('graph');
        // eslint-disable-next-line new-cap
        graphRef.current = ForceGraph()(elem)
            .linkLabel('score')
            .linkColor(() => '#a6a6a6')
            .nodeColor(() => '#5700c9')
            .width(elem.clientWidth)
            .height(elem.clientHeight / 2)
            ;
    }, []);

    useEffect(() => {

        let nodes = selectedWords.map((wordObj, i) => {
            return {
                id: i,
                name: wordObj.sentence,
            };
        });

        let links = [];
        for (let i = 0; i < selectedWords.length; i++) {
            for (let j = i + 1; j < selectedWords.length; j++) {
                links.push({
                    source: i,
                    target: j,
                    score: cosineSimilarity(selectedWords[i].embedding, selectedWords[j].embedding)
                });
            }
        }

        // Sort links by score, highest first
        links.sort((a, b) => b.score - a.score);

        // Keep same amount of links as nodes

        links = links.slice(0, nodes.length);

        let graphData = {
            nodes,
            links,
        };
        graphRef.current.graphData(graphData);

        // graphRef.current.d3Force('link').distance(link => Math.exp(link.score + 1) * 10);


    }, [selectedWords]);



    return <div id="graph"></div>;
};


VisualizationGraph.propTypes = {
    selectedWords: PropTypes.array.isRequired,
    word: PropTypes.string,
};

export default VisualizationGraph;
