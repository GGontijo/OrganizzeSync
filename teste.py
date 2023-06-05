from difflib import SequenceMatcher

def string_similarity(string1, string2):
    similarity = SequenceMatcher(None, string1, string2).ratio()
    return similarity

def group_similar_strings(strings, threshold):
    groups = []
    for string in strings:
        found_group = False
        for group in groups:
            for existing_string in group:
                if string_similarity(string, existing_string) >= threshold:
                    group.append(string)
                    found_group = True
                    break
            if found_group:
                break
        if not found_group:
            groups.append([string])
    return groups

strings = ["Hello", "Helo", "Hi", "Hola", "Hey", "Howdy"]
similarity_threshold = 0.8

string_groups = group_similar_strings(strings, similarity_threshold)

print("Grupos de strings:")
for group in string_groups:
    print(group)
