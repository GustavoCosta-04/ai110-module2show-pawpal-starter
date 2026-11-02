# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For the initial design of PawPal+, I decided to organize the application around four main classes: Owner, Pet, Task, and Scheduler.

The Owner class represents the person responsible for managing their pets. It stores basic information such as the owner's ID, name, email, and registered pets. The Pet class represents each individual animal and stores information such as its ID, name, species, age, owner ID, and associated tasks.

The Task class represents individual pet care activities, including feeding, walking, medication, and veterinary appointments. Each task contains information about its title, type, scheduled date and time, priority, and completion status.

Finally, the Scheduler class is responsible for managing and organizing tasks. It will eventually allow the application to sort activities, identify scheduling conflicts, retrieve daily schedules, and generate recurring tasks.

I chose this structure because separating responsibilities into different classes makes the application easier to understand, maintain, and expand. Each class has a specific purpose, while their relationships allow the different parts of the application to work together.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

No nothing really changed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff in my scheduling system is that conflict detection only identifies tasks scheduled at the exact same date and time. This approach makes the algorithm simpler and more efficient because it groups tasks using a dictionary instead of comparing every possible pair of tasks. The dictionary-based approach has an average time complexity of O(n) for grouping tasks, although sorting the conflicting time slots adds additional overhead.

However, this approach does not detect overlapping tasks with different start times. For example, if a 60-minute walk begins at 8:00 AM and another task begins at 8:30 AM, the system will not identify a conflict. Detecting these situations would require adding task duration information and implementing more advanced overlap calculations. I decided to keep exact-time conflict detection because it provides useful functionality while keeping the system simple and understandable.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
