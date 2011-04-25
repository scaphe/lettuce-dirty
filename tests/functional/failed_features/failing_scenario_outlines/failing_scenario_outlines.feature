Feature: Addition
  In order to test failing steps

  Scenario Outline: Pretend to add two numbers
    Given I have entered <input_1> into the calculator
    When I press <button>
    Then the result should be <output> on the screen

  Examples:
    | input_1 | button | output |
    | 20      | add    | 50     |
    | 2       | fail   | 7      |
    | 0       | add    | 40     |


  Scenario: failing scenario 4
    Given I have a working step
    When I have another working step
    Then I have a breaking step
