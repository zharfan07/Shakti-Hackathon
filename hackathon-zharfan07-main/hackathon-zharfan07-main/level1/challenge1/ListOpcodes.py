opcodes = []
symbols = [":", ";", "!", "?", ",", "@", "#", "$", "_"]

with open("/home/vsysuser/workspace/hackathon-zharfan07/level1/challenge1/test.S", "r") as f1, \
     open("all_opcodes.txt", "w") as f2:

    for line in f1:
        words = line.strip().split()
        if words:
            first_word = words[0]
            if any(sym in first_word for sym in symbols):
                continue
            if first_word not in opcodes:   # avoid duplicates
                opcodes.append(first_word)

    for word in sorted(opcodes):
        f2.write(word + "\n")
