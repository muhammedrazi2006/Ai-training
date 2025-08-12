def load_questions():
    with open("questions.txt", "r") as f:
        blocks = f.read().strip().split("\n\n")
        return [block.strip().split("\n") for block in blocks[:10]] # Limit to first 10 questions and also it splits by double newlines and removes extra spaces

def update_leaderboard(name, score):
    with open("leaderboard.txt", "a") as lb:
        lb.write(f"{name}:{score}\n")

def show_leaderboard():
    print("\n🏆 Final Leaderboard 🏆")
    try:
        with open("leaderboard.txt", "r") as lb:
            scores = [line.strip().split(":") for line in lb.readlines()]    # Split each line into name and score
            scores = [(name, int(score)) for name, score in scores]    # Convert scores to integers
            scores.sort(key=lambda x: x[1], reverse=True)           # Sort by score descending
            for i, (name, score) in enumerate(scores[:5], start=1):  # Show top 5 scores
                print(f"{i}. {name} - {score}")
    except FileNotFoundError:
        print("No scores yet.")

def run_quiz(name):
    questions = load_questions()
    score = 0

    print(f"\n🎮 Starting quiz for {name}")
    for q in questions:
        print(f"\n{name}'s Question: {q[0]}")
        for opt in q[1:5]:  # Assuming options are in lines 1-4
            print(opt)
        ans = input(f"{name}, Answer (a/b/c/d): ").strip().lower()
        correct = q[5].split(":")[1].strip().lower() 
        if ans == correct:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Wrong! Correct Answer: {correct}")

    print(f"\n🎯 {name}, Your Score: {score} / {len(questions)}")
    update_leaderboard(name, score)

def start_multiplayer():
    
    with open("leaderboard.txt", "w") as lb: # Clear the leaderboard file before starting a new game
        lb.write("")

    num_players = int(input("Enter number of players: "))
    player_names = []

    for i in range(num_players):
        name = input(f"Enter player name {i+1}: ")
        player_names.append(name)

    for name in player_names: # Run the quiz for each player
        run_quiz(name)

    show_leaderboard()

start_multiplayer()    

