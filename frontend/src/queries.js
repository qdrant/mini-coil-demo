import { axiosInstance as axios } from './common/axios.js';


export const queryEmbeddings = function (sentence) {
  
  /*
  Response example:

  {
    "result": [
      {
        "word": "world",
        "forms": [
          "worlds"
        ],
        "count": 1,
        "word_id": 20,
        "embedding": [
          0.8034816980361938,
          0.5176542401313782,
          0.568328320980072,
          0.2517743408679962
        ]
      },
      {
        "word": "hello",
        "forms": [
          "hello"
        ],
        "count": 1,
        "word_id": 1893,
        "embedding": [
          -0.34344425797462463,
          0.6368343830108643,
          0.3761855959892273,
          0.08485057950019836
        ]
      },
      {
        "word": "[CLS]",
        "forms": [
          "[CLS]"
        ],
        "count": 1,
        "word_id": -1,
        "embedding": [
          1
        ]
      },
      {
        "word": "[SEP]",
        "forms": [
          "[SEP]"
        ],
        "count": 1,
        "word_id": -1,
        "embedding": [
          1
        ]
      }
    ]
  }
  */
  
  return axios.get('/api/embed', { params: { query: sentence } })
    .then((response) => {

      let processedResponse = {};

      /// Collect mapping from the word form to the embedding. Skip words with word_id == -1.
      /// Example output

      /*
      {
        "worlds": {
          "word": "world",
          "embedding": [0.8034816980361938, 0.5176542401313782, 0.568328320980072, 0.2517743408679962],
          "count": 1,
          "word_id": 20
        },
        "hello": {
          "word": "hello",
          "embedding": [-0.34344425797462463, 0.6368343830108643, 0.3761855959892273, 0.08485057950019836],
          "count": 1,
          "word_id": 1893
        }
      }
      */
      
      response.data.result.forEach((wordObj) => {
        if (wordObj.word_id !== -1) {
          for (let form of wordObj.forms) {
            processedResponse[form] = {
              word: wordObj.word,
              embedding: wordObj.embedding,
              count: wordObj.count,
              word_id: wordObj.word_id
            };
          }
        }
      });

      return processedResponse;
    });
};
