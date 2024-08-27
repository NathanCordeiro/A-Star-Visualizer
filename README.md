# A* Pathfinding Visualizer

This project is a visualizer for the A* pathfinding algorithm implemented using Python and PyQt5. The visualizer allows users to see how the A* algorithm finds the shortest path from a start node to a goal node on a grid.

## Features

| Feature                 | Description                                                        |
|-------------------------|--------------------------------------------------------------------|
| Start and Goal Nodes    | Users can set start and goal nodes to visualize the pathfinding.   |
| Heuristic Calculation   | Utilizes Chebyshev distance as the heuristic for pathfinding.      |
| Dynamic Grid Size       | The grid size can be adjusted, defaulting to 10x10 cells.          |
| Visual Feedback         | Displays different colors for empty cells, start, goal, and path.  |
| Open/Closed Sets        | Efficient management of nodes using open and closed sets.          |
| Diagonal Movement       | Supports diagonal movement with appropriate cost adjustments.      |
| Real-time Visualization | The algorithm steps can be visualized in real-time with delays.    |

## Installation

To run the A* Pathfinding Visualizer, you need to have Python installed along with the required dependencies.

1. Clone the repository:
    ```bash
    git clone https://github.com/NathanCordeiro/A-Star-Visualizer.git
    cd A-Star-Visualizer
    ```

2. Install the required dependencies:
    ```bash
    pip install PyQt5
    ```

3. Run the visualizer:
    ```bash
    python main.py
    ```

## Usage

- **Start the Visualization**: When you run the script, it will automatically start visualizing the A* algorithm's steps to find the shortest path.
- **Modify Grid**: You can modify the grid size, start, and goal positions by editing the parameters in the `GridWidget` class in `main.py`.
- **Visualization Controls**: The visualization can be paused or restarted by interacting with the GUI elements.

## Notes

- The visualization speed can be adjusted by modifying the timer interval in the `GridWidget` class (`self.timer.start(100)`). The value is in milliseconds.
- The heuristic function is set to use the Chebyshev distance, which considers the maximum distance in either the horizontal or vertical direction. This makes it suitable for grids allowing diagonal movements.
- If the grid size is increased, consider optimizing the open set management further to handle larger datasets more efficiently.

## Important

- Ensure that PyQt5 is installed correctly, as it is required to run the GUI for this visualizer.
- The current implementation uses a simple heuristic and may need adjustments for more complex environments or different types of terrain.

## License

[![Licence](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE)
