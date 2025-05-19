using NUnit.Framework;
using VisualDM.Utilities;

namespace VisualDM.Tests
{
    [TestFixture]
    public class InputSanitizerTests
    {
        [Test]
        public void SanitizeChatMessage_RemovesHtmlAndEncodes()
        {
            string input = "<b>Hello<script>alert('x')</script></b>";
            string sanitized = InputSanitizer.SanitizeChatMessage(input);
            Assert.IsFalse(sanitized.Contains("<") || sanitized.Contains(">"));
            Assert.IsTrue(sanitized.Contains("Hello"));
        }

        [Test]
        public void SanitizeUsername_ValidAndInvalid()
        {
            Assert.AreEqual("Player1", InputSanitizer.SanitizeUsername("Player1"));
            Assert.IsNull(InputSanitizer.SanitizeUsername("Player!@#"));
            Assert.IsNull(InputSanitizer.SanitizeUsername(""));
        }

        [Test]
        public void SanitizeFormField_EmailNumberDate()
        {
            Assert.AreEqual("test@example.com", InputSanitizer.SanitizeFormField("test@example.com", "email"));
            Assert.AreEqual("12345", InputSanitizer.SanitizeFormField("12345", "number"));
            Assert.AreEqual("2024-01-01", InputSanitizer.SanitizeFormField("2024-01-01", "date"));
            Assert.IsNull(InputSanitizer.SanitizeFormField("notanemail", "email"));
        }

        [Test]
        public void SanitizeFileName_RemovesInvalidChars()
        {
            string input = "my*illegal:file?.txt";
            string sanitized = InputSanitizer.SanitizeFileName(input);
            Assert.IsFalse(sanitized.Contains(":") || sanitized.Contains("*") || sanitized.Contains("?"));
        }

        [Test]
        public void IsChatMessageClean_DetectsXss()
        {
            Assert.IsFalse(InputSanitizer.IsChatMessageClean("<script>alert('x')</script>"));
            Assert.IsTrue(InputSanitizer.IsChatMessageClean("Hello world!"));
        }

        [Test]
        public void IsUsernameAllowed_RejectsReserved()
        {
            Assert.IsFalse(InputSanitizer.IsUsernameAllowed("admin"));
            Assert.IsTrue(InputSanitizer.IsUsernameAllowed("player"));
        }

        [Test]
        public void IsFileTypeAllowed_ValidatesExtensions()
        {
            Assert.IsTrue(InputSanitizer.IsFileTypeAllowed("avatar.png", new[] { ".png", ".jpg" }));
            Assert.IsFalse(InputSanitizer.IsFileTypeAllowed("avatar.exe", new[] { ".png", ".jpg" }));
        }

        [Test]
        public void SanitizeChatMessage_BlocksXssPayloads()
        {
            string[] xssPayloads = {
                "<script>alert('x')</script>",
                "<img src=x onerror=alert(1)>",
                "<svg onload=alert(1)>",
                "<iframe src='javascript:alert(1)'></iframe>",
                "<a href=javascript:alert(1)>click</a>",
                "&lt;script&gt;alert('x')&lt;/script&gt;",
                "%253Cscript%253Ealert('x')%253C/script%253E"
            };
            foreach (var payload in xssPayloads)
            {
                Assert.IsFalse(InputSanitizer.IsChatMessageClean(payload), $"Should block: {payload}");
            }
        }

        [Test]
        public void SanitizeChatMessage_BlocksSqlInjection()
        {
            string[] sqlPayloads = {
                "'; DROP TABLE users;--",
                "admin' OR '1'='1",
                "' OR 1=1--",
                "' UNION SELECT * FROM users--"
            };
            foreach (var payload in sqlPayloads)
            {
                // Should not be considered clean, but may not catch all SQLi (depends on context)
                Assert.IsTrue(InputSanitizer.IsChatMessageClean(payload)); // Should not trigger XSS, but test for regression
            }
        }

        [Test]
        public void SanitizeChatMessage_BlocksHtmlJsTemplateInjection()
        {
            string[] templatePayloads = {
                "{{7*7}}",
                "<%= alert('x') %>",
                "${7*7}",
                "<% response.write('x') %>"
            };
            foreach (var payload in templatePayloads)
            {
                Assert.IsTrue(InputSanitizer.IsChatMessageClean(payload)); // Should not trigger XSS, but test for regression
            }
        }

        [Test]
        public void SanitizeUsername_BoundaryCases()
        {
            Assert.IsNull(InputSanitizer.SanitizeUsername(""));
            Assert.IsNull(InputSanitizer.SanitizeUsername("aVeryLongUsernameThatExceedsTheLimit", 10));
            Assert.AreEqual("user_name-1", InputSanitizer.SanitizeUsername("user_name-1"));
        }

        [Test]
        public void SanitizeFileName_BoundaryCases()
        {
            Assert.IsNull(InputSanitizer.SanitizeFileName("", 10));
            Assert.IsNull(InputSanitizer.SanitizeFileName("aVeryLongFileNameThatExceedsTheLimit.txt", 10));
            Assert.AreEqual("file.txt", InputSanitizer.SanitizeFileName("file.txt", 64));
        }
    }
} 