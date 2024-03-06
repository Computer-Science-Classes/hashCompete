# src/hash_word_set.py
class Node:
    def __init__(self, word):
        self.word = word
        self.next = None

class HashWordSet:
    BUCKETS = 53

    def __init__(self, vowel_multiplier=2, endings_multiplier=4, consonant_multiplier=2, frequency_multiplier=2):
        self.elementData = [None] * self.BUCKETS
        self.size = 0
        self.vowel_multiplier = vowel_multiplier
        self.endings_multiplier = endings_multiplier
        self.consonant_multiplier = consonant_multiplier
        self.frequency_multiplier = frequency_multiplier

    def normalize(self, word):
        specialChars = " ~!@#$%^&*()_+`-={}[]|\\:\";'<>?,./â€œâ€�â„¢"
        i = 0
        while i < len(word) and word[i] in specialChars:
            i += 1
        j = len(word) - 1
        while j > i and word[j] in specialChars:
            j -= 1
        return word[i:j+1].upper()
    
    def contains(self, word):
        h = self.hash(word)
        current = self.elementData[h]
        while current is not None:
            if current.word == word:
                return True
            current = current.next
        return False
    
    def add(self, word):
        normWord = self.normalize(word)
        if not self.contains(normWord):
            h = self.hash(normWord)
            newNode = Node(normWord)
            newNode.next = self.elementData[h]
            self.elementData[h] = newNode
            self.size += 1

    # def hash(self, word):
    #     hash = 0
    #     prime = 31
    #     #length_multiplier = 1 + len(word) / 100
    #     for i, char in enumerate(word):
    #         charValue = ord(word[i])

    #         # Vowel multiplier
    #         if word[i] in "AEIOUaeiou":
    #             charValue = int(charValue * self.vowel_multiplier)

    #         # Endings multiplier
    #         if i == len(word) - 2 or i == len(word) - 3:
    #             charValue = int(charValue * self.endings_multiplier)

    #         # Consonant multiplier
    #         if char.lower() in "bcdfghjklmnpqrstvwxyz":
    #             charValue = int(charValue * self.consonant_multiplier)

    #         # Frequency-based multiplier
    #         if char.lower() in "eario":
    #             charValue = int(charValue * self.frequency_multiplier)

    #         hash = (hash * prime + charValue) % self.BUCKETS
    #     return int(hash)
            
    def hash(self, word):
        hash = 0
        prime = 31
        #length_multiplier = 1 + len(word) / 100
        for i, char in enumerate(word):
            charValue = ord(word[i])

            # Vowel multiplier
            if word[i] in "AEIOUaeiou":
                charValue *= 2

            # Endings multiplier
            if i == len(word) - 2 or i == len(word) - 3:
                charValue *=  4

            # # Consonant multiplier
            # if char.lower() in "bcdfghjklmnpqrstvwxyz":
            #     charValue = int(charValue * 4)

            # # Frequency-based multiplier
            # if char.lower() in "eario":
            #     charValue = int(charValue * 4)

            hash = (hash * prime + charValue) % self.BUCKETS
        return int(hash)
    
    def efficiency_factor(self):
        minLength = float('inf')
        avgLength = int(self.size / self.BUCKETS)
        maxLength = float('-inf')
        efficiencyFactor = 0.0

        for n in self.elementData:
            length = 0
            while n is not None:
                length += 1
                n = n.next
            minLength = min(minLength, length)
            maxLength = max(maxLength, length)
            efficiencyFactor += (length - avgLength) ** 2

        efficiencyFactor /= self.BUCKETS
        return {
            "size": self.size,
            "minLength": minLength,
            "avgLength": avgLength,
            "maxLength": maxLength,
            "efficiencyFactor": efficiencyFactor
        }
    
    def __str__(self):
        ef = self.efficiency_factor()
        output = f'size = {ef["size"]}\n'
        output += f'minLength = {ef["minLength"]}\n'
        output += f'avgLength = {ef["avgLength"]}\n'
        output += f'maxLength = {ef["maxLength"]}\n'
        output += f'efficiencyFactor = {ef["efficiencyFactor"]}'
        return output
    
def read_book_and_calculate_hash(book_file):
    print("Hello to the Hashing competition!")

    hash_set = HashWordSet()
    with open(book_file, 'r', encoding='utf-8') as file:
        for line in file:
            for word in line.split():
                hash_set.add(word)

    print(hash_set)
    print("Goodbye!")

book_file = "books/pride_and_prejudice.txt"
read_book_and_calculate_hash(book_file)