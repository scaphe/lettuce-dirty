Feature: Test failed steps

  Scenario: failing scenario 1
    Given I have a working step
    When I have another working step
    Then I have a breaking step

  Scenario: failing scenario 2
    Given I have a working step
    When I have another working step
    Then I have a breaking step

  Scenario: working scenario 3
    Given I have a working step
    When I have another working step
    Then I have a working step

  Scenario: working scenario 4
    Given I have a working step
    When I have another working step
    Then I have a working step

  Scenario: failing scenario 5
    Given I have a working step
    When I have another working step
    Then I have a breaking step
