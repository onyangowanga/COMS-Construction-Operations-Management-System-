import re

# Read the file
with open('COMS/frontend/app/system-admin/notifications/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace literal \n with actual newlines everywhere
content = content.replace('\\n', '\n')

# Replace Modal component with div-based modal
content = content.replace(
    '<Modal\n      isOpen={true}\n      onClose={onClose}\n      title={template ? \'Edit Template\' : \'Create Template\'}\n    >',
    '<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">\n      <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">\n        <div className="flex justify-between items-center mb-4">\n          <h2 className="text-lg font-semibold">\n            {template ? \'Edit Template\' : \'Create Template\'}\n          </h2>\n          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">\n            <X className="h-5 w-5" />\n          </button>\n        </div>'
)

content = content.replace(
    '</Modal>',
    '</div>\n    </div>'
)

# Write back
with open('COMS/frontend/app/system-admin/notifications/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Notifications file fixed')

# Now fix security file - add missing closing brace
with open('COMS/frontend/app/settings/security/page.tsx', 'r', encoding='utf-8') as f:
    sec_content = f.read()

if not sec_content.rstrip().endswith('}'):
    sec_content = sec_content.rstrip() + '\n}\n'
    with open('COMS/frontend/app/settings/security/page.tsx', 'w', encoding='utf-8') as f:
        f.write(sec_content)
    print('✓ Security file fixed - added closing brace')
else:
    print('✓ Security file already complete')
