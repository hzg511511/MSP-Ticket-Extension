const fc = require("fast-check");
const { validateForm } = require("../popup.js");

const FIELDS = ["creator", "userIssue", "issueCause", "issueSolution"];
const nonempty = fc.string({ minLength: 1 }).filter(s => s.trim() !== "");

test("全部非空时 valid=true", () => {
  fc.assert(fc.property(nonempty, nonempty, nonempty, nonempty, (a, b, c, d) => {
    const { valid, errors } = validateForm({ creator: a, userIssue: b, issueCause: c, issueSolution: d });
    return valid === true && Object.keys(errors).length === 0;
  }));
});

test("空白字段时 valid=false 且 errors 包含该字段", () => {
  fc.assert(fc.property(fc.constantFrom(...FIELDS), (emptyField) => {
    const data = { creator: "a", userIssue: "b", issueCause: "c", issueSolution: "d" };
    data[emptyField] = "   ";
    const { valid, errors } = validateForm(data);
    return valid === false && emptyField in errors;
  }));
});
