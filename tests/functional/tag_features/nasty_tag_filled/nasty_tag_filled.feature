@primary @purple @orange
Feature: Test with multiple @tagged steps

  @red
  Scenario: red scenario with tags in the scenario @name
    Running "red" scenario

  @blue
  Scenario: blue scenario
    Running "blue" scenario

  @red @blue
  Scenario: purple scenario
    Running "purple" scenario

  @black
  Scenario Outline: black scenario
    Running "black" scenario <again>
    
    Examples
    | again |
    | @darn tags |

