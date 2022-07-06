# R: This program was meant for the book called "Moscow Puzzles" which had these roman numerals as chapters.
# R: In order to get a random chapter, I just used this litle script.
from random import choices

# R: Get a random roman numeral from a list
def main():
    puzzles = ["I", "II", "III", "IV", "V", "VI", "VII", "IX", "X", "XI", "XII", "XIII", "XIV"]
    print(choices(puzzles)[0])
    return

if __name__ == "__main__":
    main()
