#=, ==, if, else, elif, and, or, not, <, >, <=, >=, !=

score = int(input("Enter your score: "))

if score >= 90:
    print("Grade A")
elif score >= 80 and score <= 89:
    print("Grade B")
elif score >= 70 and score <= 79:
    print("Grade C")
else:
    print("Failed")