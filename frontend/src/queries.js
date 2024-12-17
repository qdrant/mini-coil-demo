export const queryEmbeddings = function (sentence) {
  // todo: replace with real API call
  return new Promise((resolve) => {
    setTimeout(() => {
      const res = sentence
        .trim()
        .split(' ')
        .reduce((acc, word, currentIndex) => {
          if (word.length && currentIndex !== 2) {
            acc[word] = {
              count: 1,
              word_id: currentIndex,
              embedding: [
                0.9681012034416199, 0.07225080579519272, 0.7214844822883606,
                0.25930842757225037,
              ],
            };
          }
          return acc;
        }, {});
      resolve(res);
    }, 1000);
  });
};
