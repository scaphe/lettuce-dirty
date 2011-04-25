Feature: Syntax check steps

  Scenario: nothing really
    Given I have a matching step
    When I do something unrecognised
    Then the syntax check should complain
    And ignore matching steps
