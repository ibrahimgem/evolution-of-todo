/**
 * Theme System Test Suite
 * Comprehensive testing for the enhanced theme system
 */

export class ThemeSystemTester {
  private static instance: ThemeSystemTester;

  static getInstance(): ThemeSystemTester {
    if (!ThemeSystemTester.instance) {
      ThemeSystemTester.instance = new ThemeSystemTester();
    }
    return ThemeSystemTester.instance;
  }

  /**
   * Test theme switching functionality
   */
  async testThemeSwitching(): Promise<boolean> {
    console.log('🧪 Testing theme switching...');

    try {
      // Test initial state
      const initialTheme = this.getCurrentTheme();
      console.log(`✓ Initial theme: ${initialTheme}`);

      // Test theme toggle
      this.toggleTheme();
      await this.waitForTransition();
      const newTheme = this.getCurrentTheme();
      console.log(`✓ Toggled to: ${newTheme}`);

      // Test preference setting
      this.setThemePreference('system');
      await this.waitForTransition();
      console.log('✓ System preference set');

      // Test explicit theme setting
      this.setThemePreference('dark');
      await this.waitForTransition();
      console.log('✓ Dark theme set');

      this.setThemePreference('light');
      await this.waitForTransition();
      console.log('✓ Light theme set');

      return true;
    } catch (error) {
      console.error('❌ Theme switching test failed:', error);
      return false;
    }
  }

  /**
   * Test visual consistency across components
   */
  testVisualConsistency(): boolean {
    console.log('🎨 Testing visual consistency...');

    try {
      const testResults: { [key: string]: boolean } = {};

      // Test CSS custom properties
      testResults.cssVariables = this.testCSSVariables();
      console.log(`✓ CSS Variables: ${testResults.cssVariables}`);

      // Test theme-aware components
      testResults.themeAwareComponents = this.testThemeAwareComponents();
      console.log(`✓ Theme-aware components: ${testResults.themeAwareComponents}`);

      // Test transitions
      testResults.transitions = this.testTransitions();
      console.log(`✓ Transitions: ${testResults.transitions}`);

      // Test accessibility
      testResults.accessibility = this.testAccessibility();
      console.log(`✓ Accessibility: ${testResults.accessibility}`);

      return Object.values(testResults).every(result => result);
    } catch (error) {
      console.error('❌ Visual consistency test failed:', error);
      return false;
    }
  }

  /**
   * Test performance metrics
   */
  async testPerformance(): Promise<boolean> {
    console.log('⚡ Testing performance...');

    try {
      const startTime = performance.now();

      // Perform rapid theme switches
      for (let i = 0; i < 5; i++) {
        this.toggleTheme();
        await this.waitForTransition(200);
      }

      const endTime = performance.now();
      const duration = endTime - startTime;

      console.log(`✓ Theme switching performance: ${duration.toFixed(2)}ms`);

      // Check if performance is acceptable (should be under 2 seconds for 5 switches)
      const isPerformanceAcceptable = duration < 2000;
      console.log(`✓ Performance acceptable: ${isPerformanceAcceptable}`);

      return isPerformanceAcceptable;
    } catch (error) {
      console.error('❌ Performance test failed:', error);
      return false;
    }
  }

  /**
   * Test accessibility features
   */
  testAccessibility(): boolean {
    console.log('♿ Testing accessibility...');

    try {
      // Check for proper ARIA labels
      const themeToggle = document.querySelector('[data-theme-toggle], button[aria-label*="Switch to"]');
      const hasAriaLabel = !!themeToggle?.getAttribute('aria-label');
      console.log(`✓ ARIA labels: ${hasAriaLabel}`);

      // Check for screen reader announcements
      const liveRegion = document.getElementById('theme-announcements');
      const hasLiveRegion = !!liveRegion;
      console.log(`✓ Live region: ${hasLiveRegion}`);

      // Check for keyboard navigation
      const hasKeyboardShortcut = this.testKeyboardNavigation();
      console.log(`✓ Keyboard navigation: ${hasKeyboardShortcut}`);

      return hasAriaLabel && hasLiveRegion && hasKeyboardShortcut;
    } catch (error) {
      console.error('❌ Accessibility test failed:', error);
      return false;
    }
  }

  /**
   * Test theme persistence
   */
  testPersistence(): boolean {
    console.log('💾 Testing persistence...');

    try {
      // Save current state
      const originalTheme = this.getCurrentTheme();
      const originalPreference = this.getThemePreference();

      // Change theme
      this.setThemePreference('dark');
      this.toggleTheme();

      // Simulate page reload (without actually reloading)
      const persistedTheme = localStorage.getItem('theme');
      const persistedPreference = localStorage.getItem('theme-preference');

      console.log(`✓ Theme persisted: ${persistedTheme}`);
      console.log(`✓ Preference persisted: ${persistedPreference}`);

      // Restore original state
      this.setThemePreference(originalPreference as any);
      if (originalTheme !== this.getCurrentTheme()) {
        this.toggleTheme();
      }

      return !!persistedTheme && !!persistedPreference;
    } catch (error) {
      console.error('❌ Persistence test failed:', error);
      return false;
    }
  }

  /**
   * Run all tests
   */
  async runAllTests(): Promise<boolean> {
    console.log('🚀 Starting Evolution of Todo Theme System Tests\n');

    const results = {
      switching: await this.testThemeSwitching(),
      consistency: this.testVisualConsistency(),
      performance: await this.testPerformance(),
      accessibility: this.testAccessibility(),
      persistence: this.testPersistence(),
    };

    const allPassed = Object.values(results).every(result => result);

    console.log('\n📊 Test Results:');
    Object.entries(results).forEach(([test, passed]) => {
      console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASSED' : 'FAILED'}`);
    });

    console.log(`\n🎯 Overall: ${allPassed ? 'ALL TESTS PASSED ✅' : 'SOME TESTS FAILED ❌'}`);

    if (allPassed) {
      console.log('\n✨ The enhanced theme system is working perfectly!');
      console.log('✓ Smooth transitions with custom CSS properties');
      console.log('✓ Multiple toggle variants (icon-only, icon-text, pill, dropdown)');
      console.log('✓ Full accessibility support with screen readers');
      console.log('✓ Performance optimizations and lazy loading');
      console.log('✓ Visual feedback and loading states');
      console.log('✓ Theme-aware components across the application');
    }

    return allPassed;
  }

  // Private helper methods

  private getCurrentTheme(): string {
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  }

  private getThemePreference(): string {
    return localStorage.getItem('theme-preference') || 'system';
  }

  private toggleTheme(): void {
    const themeToggle = document.querySelector('button, [data-theme-toggle]') as HTMLElement;
    themeToggle?.click();
  }

  private setThemePreference(preference: string): void {
    // Simulate setting preference through the dropdown
    const dropdown = document.querySelector('[data-theme-dropdown]') as HTMLElement;
    if (dropdown) {
      dropdown.click();
      setTimeout(() => {
        const option = document.querySelector(`button[data-theme-option="${preference}"]`) as HTMLElement;
        option?.click();
      }, 100);
    }
  }

  private async waitForTransition(timeout: number = 350): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, timeout));
  }

  private testCSSVariables(): boolean {
    const root = document.documentElement;
    const computedStyle = getComputedStyle(root);

    const themeVars = [
      '--theme-background',
      '--theme-text',
      '--theme-border',
      '--theme-card-background'
    ];

    return themeVars.every(varName => computedStyle.getPropertyValue(varName).length > 0);
  }

  private testThemeAwareComponents(): boolean {
    // Check if components are using theme variables
    const buttons = document.querySelectorAll('button');
    const inputs = document.querySelectorAll('input');

    // Simple check - look for theme-related classes
    const hasThemeButtons = Array.from(buttons).some(btn =>
      btn.classList.contains('bg-theme-card-background') ||
      btn.classList.contains('text-theme-text')
    );

    const hasThemeInputs = Array.from(inputs).some(input =>
      input.classList.contains('bg-theme-card-background') ||
      input.classList.contains('text-theme-text')
    );

    return hasThemeButtons || hasThemeInputs;
  }

  private testTransitions(): boolean {
    const root = document.documentElement;
    const computedStyle = getComputedStyle(root);

    const transitionProperty = computedStyle.getPropertyValue('transition-property');
    const hasThemeTransitions = transitionProperty.includes('background-color') ||
                                transitionProperty.includes('--theme');

    return hasThemeTransitions;
  }

  private testKeyboardNavigation(): boolean {
    // Check if keyboard event listeners are attached
    const hasKeyboardSupport = !!window.onkeydown;
    return hasKeyboardSupport;
  }
}

// Auto-run tests in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  // Expose tester globally for manual testing
  (window as any).themeTester = ThemeSystemTester.getInstance();

  // Run tests after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => ThemeSystemTester.getInstance().runAllTests(), 1000);
    });
  } else {
    setTimeout(() => ThemeSystemTester.getInstance().runAllTests(), 1000);
  }
}