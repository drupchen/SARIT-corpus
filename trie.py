class Node:
    def __init__(self, label=None, match=False):
        self.label = label
        self.match = match
        self.children = dict()

    def addChild(self, key, match=False):
        if not isinstance(key, Node):
            self.children[key] = Node(key, match)
        else:
            self.children[key.match] = key

    def __getitem__(self, key):
        return self.children[key]


class Trie:
    def __init__(self):
        self.head = Node()

    def __getitem__(self, key):
        return self.head.children[key]

    def add(self, word):
        current_node = self.head
        word_finished = True

        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break

        # For ever new letter, create a new child node
        if not word_finished:
            while i < len(word):
                current_node.addChild(word[i])
                current_node = current_node.children[word[i]]
                i += 1

        # Let's store the full word at the end node so we don't need to
        # travel back up the tree to reconstruct the word
        current_node.match = True

    def walk(self, char, current_node=None):
        if not current_node:
            current_node = self.head

        if char in current_node.children:
            next_node = current_node[char]
        else:
            next_node = None

        match = current_node.match

        return next_node, match

    def has_word(self, word):
        if word == '':
            return False
        if word == None:
            raise ValueError('Trie.has_word requires a not-Null string')

        # Start at the top
        current_node = self.head
        exists = True
        for letter in word:
            if letter in current_node.children:
                current_node = current_node.children[letter]
            else:
                exists = False
                break

        # Still need to check if we just reached a word like 't'
        # that isn't actually a full word in our dictionary
        if exists:
            if current_node.match == False:
                exists = False

        return exists

    def find_matches(self, in_str, res):
        """

        :param (string) in_str: input string
        :param (dict) res: the matches with the indices for each match are stored in this dict
        """
        start = 0
        matches = []
        current_node = None
        for i, c in enumerate(in_str):

            if current_node:
                current_node, match = self.walk(c, current_node)
            else:
                current_node, match = self.walk(c, self.head)

            # add non-maximal matches
            if match:
                matches.append(i)

            # take longest match
            if not current_node and matches != []:
                keys = [(start, m) for m in matches]
                for key in keys:
                    key_str = in_str[key[0]:key[1]+1]
                    if key_str not in res.keys():
                        res[key_str] = [key]
                    else:
                        res[key_str].append(key)

            # update vars
            if not current_node:
                if matches != []:
                    matches = []
                start = i + 1


if __name__ == '__main__':
    """ Example use """
    trie = Trie()
    words = 'hello goodbye help gerald gold tea ted team to too tom stan standard money'
    for word in words.split():
        trie.add(word)
    print("'goodbye' in trie: ", trie.has_word('goodbye'))
    print(trie.walk('g'))
    # print(trie.start_with_prefix('g'))
    # print(trie.start_with_prefix('to'))
