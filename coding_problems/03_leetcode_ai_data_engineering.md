# Level 3: AI & Data Engineering (Problems 21-30)

Handling large datasets, performing statistical matrix operations, and preparing strings for Large Language Models (LLMs) are core tasks for AI Engineering. Practice these mathematical algorithms.

---

### Problem 21: Vector Dot Product
**Difficulty:** Easy | **Topic:** Arrays, Math

**Description:**
The dot product is the foundation of almost all AI and embedding models, measuring how similar two vectors are.
Given two integer arrays `vectorA` and `vectorB` of the exact same length, calculate and return their dot product. The dot product is the sum of the products of their corresponding entries.

**Constraints:**
- `1 <= len(vectorA) == len(vectorB) <= 10^5`
- `-100 <= vectorA[i], vectorB[i] <= 100`

**Example 1:**
```python
Input: vectorA = [1, 2, 3], vectorB = [4, 5, 6]
Output: 32
Explanation: (1*4) + (2*5) + (3*6) = 4 + 10 + 18 = 32.
```

**Starter Code:**
```python
def dot_product(vectorA: list[int], vectorB: list[int]) -> int:
    pass
```

**AI Engineer Hint:** You can iterate through using an index `for i in range(len(vectorA)):`, or Pythonically use `zip(vectorA, vectorB)`.

---

### Problem 22: Step Function Activation
**Difficulty:** Easy | **Topic:** Logic Arrays

**Description:**
Early neural networks (Perceptrons) used a simple "Step Fuction" to decide if a neuron fired. 
You are given a list of `inputs`, a list of `weights`, and an integer `bias`. Calculate the dot product of the inputs and weights, and then add the bias. If the final result is `>= 0`, return `1`. Otherwise, return `0`.

**Constraints:**
- `len(inputs) == len(weights) <= 10^4`

**Example 1:**
```python
Input: inputs = [1.0, 0.5], weights = [0.2, -0.1], bias = -0.1
Output: 1
Explanation: (1.0*0.2) + (0.5*-0.1) - 0.1 = 0.2 - 0.05 - 0.1 = 0.05. Since 0.05 >= 0, return 1.
```

**Starter Code:**
```python
def activation_step(inputs: list[float], weights: list[float], bias: float) -> int:
    pass
```

**AI Engineer Hint:** Re-use the logic from Problem 21, but apply a boolean conditional return at the very end.

---

### Problem 23: The K-Means Centroid Assigner
**Difficulty:** Medium | **Topic:** Coordinate Math, Clustering

**Description:**
K-Means Clustering groups data together into clusters.
You are given a 2D array `points` where each point is `[x, y]`, and a 2D array `centroids` which represent the center coordinates of existing clusters.
For every point, find the index of the centroid that is closest to it (using basic Euclidean distance squared to avoid floating point math: `(x1-x2)^2 + (y1-y2)^2`). Return an array of these indexes.

**Constraints:**
- `1 <= len(points) <= 10^4`
- `1 <= len(centroids) <= 100`

**Example 1:**
```python
Input: points = [[1,1], [9,9], [1,2]], centroids = [[0,0], [10,10]]
Output: [0, 1, 0]
Explanation: [1,1] is closest to [0,0] (Index 0). [9,9] is closest to [10,10] (Index 1). [1,2] is closest to [0,0] (Index 0).
```

**Starter Code:**
```python
def assign_clusters(points: list[list[int]], centroids: list[list[int]]) -> list[int]:
    pass
```

**AI Engineer Hint:** For each point, calculate the distance to ALL centroids. Keep track of the `min_distance` and the `best_index` associated with it.

---

### Problem 24: Early Stopping (Training Loop Break)
**Difficulty:** Easy | **Topic:** Loop Control logic

**Description:**
If you train an AI too long, it will overfit (memorize the data). We use "Early Stopping" to break the loop if the model stops improving.
You are given a list of `losses` (representing the model's error rate at each epoch) and an integer `patience`.
Iterate through the array. If the model's loss strictly increases or stays the same for `patience` consecutive epochs, immediately return the index (epoch) where training stopped. If it finishes the array safely, return `-1`.

**Constraints:**
- `1 <= len(losses) <= 100`

**Example 1:**
```python
Input: losses = [10, 8, 5, 5, 6, 4], patience = 2
Output: 4
Explanation: Loss improved from 10->8->5. Then epoch 3 it stayed 5. Epoch 4 it rose to 6. It failed to improve for 2 consecutive epochs. Stoped at index 4.
```

**Starter Code:**
```python
def early_stopping(losses: list[int], patience: int) -> int:
    pass
```

**AI Engineer Hint:** Track `best_loss` and `strikes`. Update `best_loss` and reset `strikes = 0` if `current_loss < best_loss`. Otherwise `strikes += 1`. Break if `strikes == patience`.

---

### Problem 25: Simple Subword Tokenizer
**Difficulty:** Medium | **Topic:** Strings, Regex

**Description:**
LLMs don't read whole words; they read "tokens." Sometimes words like "walking" are split into "walk" and "ing".
Given a sentence string, and a list of `suffixes` (e.g., `["ing", "ed", "ly"]`), break the string into an array of words. However, if a word ends with any suffix in the list, split the suffix out into its own separate token.

**Constraints:**
- Words are separated by exactly one space. No punctuation.

**Example 1:**
```python
Input: sentence = "i am walking quickly", suffixes = ["ing", "ly"]
Output: ["i", "am", "walk", "ing", "quick", "ly"]
```

**Starter Code:**
```python
def tokenize_sentence(sentence: str, suffixes: list[str]) -> list[str]:
    pass
```

**AI Engineer Hint:** Split the string by spaces. Iterate through the words. `if word.endswith(suf):` slice the strings and append both `word[:-len(suf)]` and `suf`.

---

### Problem 26: Outlier Detector (Z-Score)
**Difficulty:** Medium | **Topic:** Statistics

**Description:**
A single malicious data point can poison an AI. Detect it using the Z-Score method!
Given a list of floats `data` representing transaction volumes, return a list of booleans indicating if each point is a "dangerous outlier." 
An outlier is defined as any point whose absolute difference from the mean is strictly greater than `3 * Standard Deviation`.

**Constraints:**
- `2 <= len(data) <= 10^4`

**Example 1:**
```python
Input: data = [10, 12, 10, 11, 1000]
Output: [False, False, False, False, True]
```

**Starter Code:**
```python
import math

def detect_outliers(data: list[float]) -> list[bool]:
    pass
```

**AI Engineer Hint:** 
1. Calculate Mean (Sum / N). 
2. Calculate Variance: `sum( (x - mean)**2 ) / N`. 
3. StdDev: `sqrt(Variance)`. 
4. Check `abs(x - mean) > 3 * std_dev`.

---

### Problem 27: The Stop Words Scrubber
**Difficulty:** Easy | **Topic:** Arrays, Set operations

**Description:**
"Stop words" like 'the', 'a', 'is' add noise to NLP models because they don't carry dense meaning. 
Given a `sentence` and a list of `stop_words`, return the sentence with all exact matches of the stop words completely removed.

**Constraints:**
- Sentence is lowercase alphabet only.

**Example 1:**
```python
Input: sentence = "the cat jumped over a lazy dog", stop_words = ["the", "a", "over"]
Output: "cat jumped lazy dog"
```

**Starter Code:**
```python
def remove_stop_words(sentence: str, stop_words: list[str]) -> str:
    pass
```

**AI Engineer Hint:** Turn `stop_words` into a `set` for O(1) searches. Split the sentence into a list, rebuild a new list `if word not in stop_set`, and `join()` it.

---

### Problem 28: Term Frequency
**Difficulty:** Easy | **Topic:** Hash Maps

**Description:**
The first part of the famous TF-IDF algorithm! 
Given a `document` (a string of words) and a `target_word`, calculate its "Term Frequency" represented as the number of times the `target_word` appears divided by the total number of words in the document.

**Constraints:**
- Document length <= 10,000 words.

**Example 1:**
```python
Input: document = "AI is cool AI is fun", target_word = "AI"
Output: 0.3333333333333333
Explanation: "AI" appears 2 times. Total words = 6. TF = 2/6 = 0.33...
```

**Starter Code:**
```python
def calculate_tf(document: str, target_word: str) -> float:
    pass
```

**AI Engineer Hint:** `split()` the document. Use `.count()` or loop through and tally, then divide by `len()`.

---

### Problem 29: Inverse Document Frequency
**Difficulty:** Medium | **Topic:** Hash Maps, Math

**Description:**
The second part of TF-IDF! 
Given a list of strings `corpus` (representing multiple documents) and a `target_word`, calculate the IDF. 
The standard formula is: `log( Total Documents / Documents containing target_word )`. If the target word does not exist in any document, return `0.0`.

**Constraints:**
- corpus length <= 1,000.

**Example 1:**
```python
Input: corpus = ["hello world", "hello AI", "goodbye AI"], target_word = "world"
Output: 1.0986122886681098
Explanation: Total docs = 3. Docs with "world" = 1. log(3/1) = 1.098...
```

**Starter Code:**
```python
import math

def calculate_idf(corpus: list[str], target_word: str) -> float:
    pass
```

**AI Engineer Hint:** Create a counter for `docs_containing = 0`. Iterate through the corpus: `if target_word in doc.split(): docs_containing += 1`. Use `math.log(total / count)`.

---

### Problem 30: Min-Max Data Scaler
**Difficulty:** Easy | **Topic:** Array Math

**Description:**
Neural networks prefer inputs that are bound between 0 and 1. 
Given a list of floats `data`, apply Min-Max scaling to every single element. 
The mathematical formula for min-max scaling a number `x` is `(x - min(data)) / (max(data) - min(data))`.
If the max and min are exactly the same, return an array of 0.0s.

**Constraints:**
- `2 <= len(data) <= 10^5`

**Example 1:**
```python
Input: data = [10.0, 20.0, 30.0]
Output: [0.0, 0.5, 1.0]
Explanation: min=10, max=30. For 20: (20-10)/(30-10) = 10/20 = 0.5.
```

**Starter Code:**
```python
def min_max_scaler(data: list[float]) -> list[float]:
    pass
```

**AI Engineer Hint:** First, find the `min_val` and `max_val` by calling `min(data)` and `max(data)` exactly ONCE so your code runs in O(N). Then use a list comprehension to calculate the array.
