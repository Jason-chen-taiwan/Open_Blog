// Theme toggle functionality
document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  const icon = themeToggle.querySelector("i");

  // Get saved theme preference
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-bs-theme", savedTheme);
  updateIcon(savedTheme);

  themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-bs-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    document.documentElement.setAttribute("data-bs-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateIcon(newTheme);
  });

  function updateIcon(theme) {
    icon.className = theme === "dark" ? "fas fa-sun" : "fas fa-moon";
  }
});

// Add fade-in animation to posts
document.addEventListener("DOMContentLoaded", () => {
  const posts = document.querySelectorAll(".post");
  posts.forEach((post) => post.classList.add("fade-in"));
});

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
});

// Back to top button functionality
document.addEventListener("DOMContentLoaded", () => {
  const backToTopButton = document.getElementById("back-to-top");

  window.onscroll = () => {
    if (
      document.body.scrollTop > 20 ||
      document.documentElement.scrollTop > 20
    ) {
      backToTopButton.style.display = "block";
    } else {
      backToTopButton.style.display = "none";
    }
  };

  backToTopButton.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
});

// Category filtering functionality
document.addEventListener("DOMContentLoaded", () => {
  const categoryLinks = document.querySelectorAll(".category-filter");
  const postsContainer = document.querySelector(".posts-list");

  categoryLinks.forEach((link) => {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      const category = e.target.dataset.category;

      // Update active state
      categoryLinks.forEach((l) => l.classList.remove("active"));
      e.target.classList.add("active");

      try {
        const response = await fetch(
          `/api/posts${category ? "?category=" + category : ""}`
        );
        if (!response.ok) throw new Error("Failed to fetch posts");

        const posts = await response.json();
        updatePosts(posts);
      } catch (error) {
        console.error("Error fetching posts:", error);
      }
    });
  });

  function updatePosts(posts) {
    if (!postsContainer) return;

    if (posts.length === 0) {
      postsContainer.innerHTML = "<p>No posts found in this category.</p>";
      return;
    }

    const postsHTML = posts
      .map(
        (post) => `
        <article class="post fade-in">
            <h2><a href="/post/${post.slug}">${post.title}</a></h2>
            <p class="meta">
                Posted on ${new Date(post.created_at).toLocaleDateString()} ${
          post.category
            ? `in <a href="#" class="category-filter" data-category="${post.category}">${post.category}</a>`
            : ""
        }
            </p>
            ${
              post.tags && post.tags.length
                ? `
                <div class="tags">
                    Tags: ${post.tags
                      .map((tag) => `<a href="#">${tag.name}</a>`)
                      .join(", ")}
                </div>
            `
                : ""
            }
            ${
              post.image_path
                ? `
                <div class="post-thumbnail mb-3">
                    <img src="/static/${post.image_path}" alt="${post.title}" class="img-fluid rounded">
                </div>
            `
                : ""
            }
            <p>${
              post.html_content
                ? post.html_content.replace(/<[^>]*>/g, "").substring(0, 200) +
                  "..."
                : ""
            }</p>
            ${
              post.is_admin
                ? `
                <div class="admin-controls">
                    <a href="/edit/${post.slug}" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-edit me-1"></i>Edit
                    </a>
                    <form action="/delete/${post.slug}" method="POST" class="d-inline">
                        <button type="submit" class="btn btn-sm btn-outline-danger" 
                                onclick="return confirm('Are you sure you want to delete this post?')">
                            <i class="fas fa-trash me-1"></i>Delete
                        </button>
                    </form>
                </div>
            `
                : ""
            }
        </article>
    `
      )
      .join("");

    postsContainer.innerHTML = postsHTML;
  }
});
