try:
    from weasyprint import HTML
    print("WeasyPrint imported successfully.")
    # Try a dummy PDF generation
    HTML(string="<h1>Test</h1>").write_pdf("test.pdf")
    print("Test PDF generated successfully.")
except Exception as e:
    print(f"Error: {e}")
