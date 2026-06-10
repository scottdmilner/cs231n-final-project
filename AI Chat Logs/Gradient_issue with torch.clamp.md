# Conversation
- conversationId: 14735ad4-a0d2-4a28-86f3-8aa8359c36b1
- endpoint: claude
- title: Gradient issue with torch.clamp
- exportAt: 00:00:55 GMT-0700 (Daylight nga Oras sa Pasipiko)

## Options
- presetId: null
- model: claude-4-5-sonnet
- resendFiles: true
- endpoint: claude
- endpointType: custom
- title: Gradient issue with torch.clamp

## History
**User**
Why does adding torch.clamp cause all the gradients to be zero?

num_epochs = 20
num_views = 4
learning_rate = 6e-2

input_tensor = torch.tensor(data_array.astype(np.float32), requires_grad=False)

batch_losses = []

density_gain = torch.ones_like(input_tensor, requires_grad=True)

optim = torch.optim.Adam([density_gain], lr=learning_rate)
# scheduler = torch.optim.lr_scheduler.ExponentialLR(optim, 0.99)

for epoch in tqdm(range(num_epochs), desc="Epochs"):
    optim.zero_grad()

    with torch.no_grad():
        density_gain = torch.clamp(density_gain.detach().clone(), 0, 100)

    print(torch.min(density_gain), torch.max(density_gain))
    dense_volume = make_dense_volume(input_tensor * density_gain)

    renderer.load_volume(volume=dense_volume)

    if (epoch % 4) == 0:
        show_preview(dense_volume, canonical_cam, fov)

    gain_acc = np.zeros(input_tensor.shape).astype(np.float32)

    for i in tqdm(range(num_views), desc="Views"):
        batch_loss = 0

        view_mat = next(cam_transform)

        renderer.render(view_mat, fov)

        volume_render = torch.tensor(np.flipud(output_image.to_numpy()).copy(), requires_grad=True)

        stylization = style_img.detach().clone()


        # plt.imshow(volume_render.detach().numpy(), cmap="gray")
        # plt.xlabel(f"Current vol; epoch: {epoch}, view: {i}")
        # plt.show()
        # plt.imshow(stylization.detach().numpy(), cmap="gray")
        # plt.xlabel(f"Masked Style; epoch: {epoch}, view: {i}")
        # plt.show()
        
        loss_fn = torch.nn.MSELoss()
        loss = loss_fn(volume_render, stylization)
        batch_loss += loss.item()

        loss.backward()

        # plt.imshow(volume_render.grad.detach().numpy())
        # plt.xlabel(f"Image Gradient; epoch: {epoch}, view: {i}")
        # plt.colorbar()
        # plt.show()

        renderer.render_volume_backward(
            view_mat=view_mat, 
            fov=fov, 
            out_grad=torch.flipud(volume_render.grad)
        )
        d_volume = renderer.get_d_volume().reshape(input_tensor.shape)
        gain_acc += d_volume

    with torch.no_grad():
        density_gain.grad = torch.tensor(gain_acc)
    
    optim.step()


    # scheduler.step()


**Anthropic**



**Anthropic**
{"type":"tool_call","tool_call":{"id":"toolu_vrtx_013wJGVjNPmTtF86rwzNnHkV","name":"web_search","args":"{\"query\":\"torch.clamp gradients zero detach clone requires_grad\"}","type":"tool_call","progress":1,"output":"=== Web Results, Turn 0 ===\n\n# Search 0: \"Detach, no_grad and requires_grad - autograd - PyTorch Forums\"\n\nAnchor: \\ue202turn0search0\nURL: https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915\nSummary: detach() detaches the output from the computationnal graph. So no gradient will be backproped along this variable. torch.no_grad says that no operation should ...\nSource: PyTorch Forums\n\n## Highlights\n\n### Highlight 1 [Relevance: 0.00]\n\n```text\n[Skip to last reply](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/24) [Skip to top](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1)\n[Skip to main content](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915#main-container)\n# [Detach, no\\_grad and requires\\_grad](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[autograd](https://discuss.pytorch.org/c/autograd/7)\n```\n\n---\n\n### Highlight 2 [Relevance: 0.00]\n\n```text\n[Skip to last reply](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/24) [Skip to top](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1)\n[Skip to main content](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915#main-container)\n# [Detach, no\\_grad and requires\\_grad](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[autograd](https://discuss.pytorch.org/c/autograd/7)\nYou have selected **0** posts.\n```\n\n---\n\n### Highlight 3 [Relevance: 0.00]\n\n```text\n[Skip to last reply](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/24) [Skip to top](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1)\n[Skip to main content](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915#main-container)\n# [Detach, no\\_grad and requires\\_grad](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[autograd](https://discuss.pytorch.org/c/autograd/7)\nYou have selected **0** posts.\n[select all](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[cancel selecting](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n```\n\n---\n\n### Highlight 4 [Relevance: 0.00]\n\n```text\n[Skip to last reply](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/24) [Skip to top](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1)\n[Skip to main content](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915#main-container)\n# [Detach, no\\_grad and requires\\_grad](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[autograd](https://discuss.pytorch.org/c/autograd/7)\nYou have selected **0** posts.\n[select all](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[cancel selecting](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[Apr 2018](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1 \"Jump to the first post\")\n```\n\n---\n\n### Highlight 5 [Relevance: 0.00]\n\n```text\n[Skip to top](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1)\n[Skip to main content](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915#main-container)\n# [Detach, no\\_grad and requires\\_grad](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[autograd](https://discuss.pytorch.org/c/autograd/7)\nYou have selected **0** posts.\n[select all](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[cancel selecting](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915)\n[Apr 2018](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/1 \"Jump to the first post\")\n1 / 23\nApr 2018\n[Jul 2022](https://discuss.pytorch.org/t/detach-no-grad-and-requires-grad/16915/24)\n```\n\n\n# Search 1: \"PyTorch preferred way to copy a tensor - Stack Overflow\"\n\nAnchor: \\ue202turn0search1\nURL: https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor\nSummary: detach() and tensor.new_tensor(x, requires_grad=True) is equivalent to x.clone().detach().requires_grad_(True). The equivalents using clone() ...\nSource: Stack Overflow\n\n## Highlights\n\n### Highlight 1 [Relevance: 0.00]\n\n```text\n##### Collectives™ on Stack Overflow\nFind centralized, trusted content and collaborate around the technologies you use most.\n[Learn more about Collectives](https://stackoverflow.com/collectives)\n**Stack Internal**\nKnowledge at work\nBring the best of human thought and AI automation together at your work.\n[Explore Stack Internal](https://stackoverflow.co/internal/?utm_medium=referral&utm_source=stackoverflow-community&utm_campaign=side-bar&utm_content=explore-teams-compact-popover)\n```\n\n---\n\n### Highlight 2 [Relevance: 0.00]\n\n```text\n##### Collectives™ on Stack Overflow\nFind centralized, trusted content and collaborate around the technologies you use most.\n[Learn more about Collectives](https://stackoverflow.com/collectives)\n**Stack Internal**\nKnowledge at work\nBring the best of human thought and AI automation together at your work.\n[Explore Stack Internal](https://stackoverflow.co/internal/?utm_medium=referral&utm_source=stackoverflow-community&utm_campaign=side-bar&utm_content=explore-teams-compact-popover)\n# [PyTorch preferred way to copy a tensor](https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor)\n```\n\n---\n\n### Highlight 3 [Relevance: 0.00]\n\n```text\n##### Collectives™ on Stack Overflow\nFind centralized, trusted content and collaborate around the technologies you use most.\n[Learn more about Collectives](https://stackoverflow.com/collectives)\n**Stack Internal**\nKnowledge at work\nBring the best of human thought and AI automation together at your work.\n[Explore Stack Internal](https://stackoverflow.co/internal/?utm_medium=referral&utm_source=stackoverflow-community&utm_campaign=side-bar&utm_content=explore-teams-compact-popover)\n# [PyTorch preferred way to copy a tensor](https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor)\n```\n\n---\n\n### Highlight 4 [Relevance: 0.00]\n\n```text\nCollectives™ on Stack Overflow\nFind centralized, trusted content and collaborate around the technologies you use most.\n[Learn more about Collectives](https://stackoverflow.com/collectives)\n**Stack Internal**\nKnowledge at work\nBring the best of human thought and AI automation together at your work.\n[Explore Stack Internal](https://stackoverflow.co/internal/?utm_medium=referral&utm_source=stackoverflow-community&utm_campaign=side-bar&utm_content=explore-teams-compact-popover)\n# [PyTorch preferred way to copy a tensor](https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor)\n[Ask Question](https://stackoverflow.com/questions/ask)\nAsked7 years, 2 months ago\nModified [1 year, 9 months ago](https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor?lastactivity \"2024-08-20 13:55:21Z\")\n```\n\n---\n\n### Highlight 5 [Relevance: 0.00]\n\n```text\nFind centralized, trusted content and collaborate around the technologies you use most.\n[Learn more about Collectives](https://stackoverflow.com/collectives)\n**Stack Internal**\nKnowledge at work\nBring the best of human thought and AI automation together at your work.\n[Explore Stack Internal](https://stackoverflow.co/internal/?utm_medium=referral&utm_source=stackoverflow-community&utm_campaign=side-bar&utm_content=explore-teams-compact-popover)\n# [PyTorch preferred way to copy a tensor](https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor)\n[Ask Question](https://stackoverflow.com/questions/ask)\nAsked7 years, 2 months ago\nModified [1 year, 9 months ago](https://stackoverflow.com/questions/55266154/pytorch-preferred-way-to-copy-a-tensor?lastactivity \"2024-08-20 13:55:21Z\")\n```\n\n\n# Search 2: \"Difference between detach, clone, and deepcopy in PyTorch tensors\"\n\nAnchor: \\ue202turn0search2\nURL: https://www.geeksforgeeks.org/deep-learning/difference-between-detach-clone-and-deepcopy-in-pytorch-tensors/\nSummary: detach() doesn't track gradients at all, as shown by the False in requires_grad. clone() tracks gradients just like the original tensor.\nSource: GeeksforGeeks\n\n## Highlights\n\n### Highlight 1 [Relevance: 0.00]\n\n```text\n[![geeksforgeeks](https://media.geeksforgeeks.org/gfg-gg-logo.svg)](https://www.geeksforgeeks.org/)\n- Courses\n- Tutorials\n- Interview Prep\nSwitch to Dark Mode\nSign In\n- [DSA](https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/)\n- [Practice Problems](https://www.geeksforgeeks.org/explore)\n- [C](https://www.geeksforgeeks.org/c/c-programming-language/)\n- [C++](https://www.geeksforgeeks.org/cpp/c-plus-plus/)\n```\n\n---\n\n### Highlight 2 [Relevance: 0.00]\n\n```text\n[![geeksforgeeks](https://media.geeksforgeeks.org/gfg-gg-logo.svg)](https://www.geeksforgeeks.org/)\n- Courses\n- Tutorials\n- Interview Prep\nSwitch to Dark Mode\nSign In\n- [DSA](https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/)\n- [Practice Problems](https://www.geeksforgeeks.org/explore)\n- [C](https://www.geeksforgeeks.org/c/c-programming-language/)\n- [C++](https://www.geeksforgeeks.org/cpp/c-plus-plus/)\n- [Java](https://www.geeksforgeeks.org/java/java/)\n```\n\n---\n\n### Highlight 3 [Relevance: 0.00]\n\n```text\n[![geeksforgeeks](https://media.geeksforgeeks.org/gfg-gg-logo.svg)](https://www.geeksforgeeks.org/)\n- Courses\n- Tutorials\n- Interview Prep\nSwitch to Dark Mode\nSign In\n- [DSA](https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/)\n- [Practice Problems](https://www.geeksforgeeks.org/explore)\n- [C](https://www.geeksforgeeks.org/c/c-programming-language/)\n- [C++](https://www.geeksforgeeks.org/cpp/c-plus-plus/)\n- [Java](https://www.geeksforgeeks.org/java/java/)\n- [Python](https://www.geeksforgeeks.org/python/python-programming-language-tutorial/)\n```\n\n---\n\n### Highlight 4 [Relevance: 0.00]\n\n```text\n[![geeksforgeeks](https://media.geeksforgeeks.org/gfg-gg-logo.svg)](https://www.geeksforgeeks.org/)\n- Courses\n- Tutorials\n- Interview Prep\nSwitch to Dark Mode\nSign In\n- [DSA](https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/)\n- [Practice Problems](https://www.geeksforgeeks.org/explore)\n- [C](https://www.geeksforgeeks.org/c/c-programming-language/)\n- [C++](https://www.geeksforgeeks.org/cpp/c-plus-plus/)\n- [Java](https://www.geeksforgeeks.org/java/java/)\n- [Python](https://www.geeksforgeeks.org/python/python-programming-language-tutorial/)\n- [JavaScript](https://www.geeksforgeeks.org/javascript/javascript-tutorial/)\n- [Data Science](https://www.geeksforgeeks.org/data-science/data-science-for-beginners/)\n```\n\n---\n\n### Highlight 5 [Relevance: 0.00]\n\n```text\nforgeeks.org/)\n- Courses\n- Tutorials\n- Interview Prep\nSwitch to Dark Mode\nSign In\n- [DSA](https://www.geeksforgeeks.org/dsa/dsa-tutorial-learn-data-structures-and-algorithms/)\n- [Practice Problems](https://www.geeksforgeeks.org/explore)\n- [C](https://www.geeksforgeeks.org/c/c-programming-language/)\n- [C++](https://www.geeksforgeeks.org/cpp/c-plus-plus/)\n- [Java](https://www.geeksforgeeks.org/java/java/)\n- [Python](https://www.geeksforgeeks.org/python/python-programming-language-tutorial/)\n- [JavaScript](https://www.geeksforgeeks.org/javascript/javascript-tutorial/)\n- [Data Science](https://www.geeksforgeeks.org/data-science/data-science-for-beginners/)\n- [Machine Learning](https://www.geeksforgeeks.org/machine-learning/machine-learning/)\n```\n\n\n# Search 3: \"5 gradient/derivative related PyTorch functions | by Attyuttam Saha\"\n\nAnchor: \\ue202turn0search3\nURL: https://attyuttam.medium.com/5-gradient-derivative-related-pytorch-functions-8fd0e02f13c6\nSummary: clone()creates a copy of tensor that imitates the original tensor's requires_grad field. We should use clone as a way to copy the tensor ...\nSource: Medium\n\n## Highlights\n\n### Highlight 1 [Relevance: 0.00]\n\n```text\n[Sitemap](https://attyuttam.medium.com/sitemap/sitemap.xml)\n[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)\nSign up\n[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fattyuttam.medium.com%\n```\n\n---\n\n### Highlight 2 [Relevance: 0.00]\n\n```text\n[Sitemap](https://attyuttam.medium.com/sitemap/sitemap.xml)\n[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)\nSign up\n[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fattyuttam.medium.com%2F5-gradient-derivative-related-pytorch-functions-8fd0e02f13c6&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)\n```\n\n---\n\n### Highlight 3 [Relevance: 0.00]\n\n```text\n[Sitemap](https://attyuttam.medium.com/sitemap/sitemap.xml)\n[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)\nSign up\n[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fattyuttam.medium.com%2F5-gradient-derivative-related-pytorch-functions-8fd0e02f13c6&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)\n[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)\n```\n\n---\n\n### Highlight 4 [Relevance: 0.00]\n\n```text\n[Sitemap](https://attyuttam.medium.com/sitemap/sitemap.xml)\n[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)\nSign up\n[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fattyuttam.medium.com%2F5-gradient-derivative-related-pytorch-functions-8fd0e02f13c6&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)\n[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)\n```\n\n---\n\n### Highlight 5 [Relevance: 0.00]\n\n```text\n[Sitemap](https://attyuttam.medium.com/sitemap/sitemap.xml)\n[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)\nSign up\n[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fattyuttam.medium.com%2F5-gradient-derivative-related-pytorch-functions-8fd0e02f13c6&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)\n[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)\nGet app\n[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)\n```\n\n\n# Search 4: \"To copy construct from a tensor, it is recommended to use ... - GitHub\"\n\nAnchor: \\ue202turn0search4\nURL: https://github.com/pytorch/pytorch/issues/59800\nSummary: clone().detach().requires_grad_(True), rather than torch.tensor(sourceTensor). value = torch.tensor(value, device=device, dtype=torch.float).\nSource: GitHub\n\n## Highlights\n\n### Highlight 1 [Relevance: 0.00]\n\n```text\n[Skip to content](https://github.com/pytorch/pytorch/issues/59800#start-of-content)\nYou signed in with another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.Dismiss alert\n```\n\n---\n\n### Highlight 2 [Relevance: 0.00]\n\n```text\n[Skip to content](https://github.com/pytorch/pytorch/issues/59800#start-of-content)\nYou signed in with another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.Dismiss alert\n{{ message }}\n[pytorch](https://github.com/pytorch)/ **[pytorch](https://github.com/pytorch/pytorch)** Public\n```\n\n---\n\n### Highlight 3 [Relevance: 0.00]\n\n```text\n[Skip to content](https://github.com/pytorch/pytorch/issues/59800#start-of-content)\nYou signed in with another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.Dismiss alert\n{{ message }}\n[pytorch](https://github.com/pytorch)/ **[pytorch](https://github.com/pytorch/pytorch)** Public\n- [Notifications](https://github.com/login?return_to=%2Fpytorch%2Fpytorch) You must be signed in to change notification settings\n```\n\n---\n\n### Highlight 4 [Relevance: 0.00]\n\n```text\n[Skip to content](https://github.com/pytorch/pytorch/issues/59800#start-of-content)\nYou signed in with another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.Dismiss alert\n{{ message }}\n[pytorch](https://github.com/pytorch)/ **[pytorch](https://github.com/pytorch/pytorch)** Public\n- [Notifications](https://github.com/login?return_to=%2Fpytorch%2Fpytorch) You must be signed in to change notification settings\n- [Fork\n27.9k](https://github.com/login?return_to=%2Fpytorch%2Fpytorch)\n```\n\n---\n\n### Highlight 5 [Relevance: 0.00]\n\n```text\ncontent](https://github.com/pytorch/pytorch/issues/59800#start-of-content)\nYou signed in with another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/pytorch/pytorch/issues/59800) to refresh your session.Dismiss alert\n{{ message }}\n[pytorch](https://github.com/pytorch)/ **[pytorch](https://github.com/pytorch/pytorch)** Public\n- [Notifications](https://github.com/login?return_to=%2Fpytorch%2Fpytorch) You must be signed in to change notification settings\n- [Fork\n27.9k](https://github.com/login?return_to=%2Fpytorch%2Fpytorch)\n```\n\n\n# Search 5: \"Why Tensor.clone().detach() is recommended when copying a tensor?\"\n\nAnchor: \\ue202turn0search5\nURL: https://stackoverflow.com/questions/62484790/why-tensor-clone-detach-is-recommended-when-copying-a-tensor\nSummary: If you have a Tensor data and want to avoid a copy, use torch.Tensor.requires_grad_() or torch.Tensor.detach(). When data is a tensor x, torch.\nSource: stackoverflow.com\n\n\n# Search 6: \"clone_module(module, memo=None) - learn2learn\"\n\nAnchor: \\ue202turn0search6\nURL: http://learn2learn.net/docs/learn2learn/\nSummary: Detaches all parameters/buffers of a previously cloned module from its computational graph. Note: detach works in-place, so it does not return a copy. Arguments.\nSource: learn2learn.net\n\n\n# Search 7: \"How to fix ? UserWarning: To copy construct from a tensor, it ... - Reddit\"\n\nAnchor: \\ue202turn0search7\nURL: https://www.reddit.com/r/learnmachinelearning/comments/132n3x4/how_to_fix_userwarning_to_copy_construct_from_a/\nSummary: UserWarning: To copy construct from a tensor, it is recommended to use sourceTensor.clone().detach(). Help.\nSource: www.reddit.com"}}


**Anthropic**
The issue is that you're breaking the computational graph by using `detach()` inside a `torch.no_grad()` context and then reassigning the result back to `density_gain`. This creates a new tensor that has no connection to the optimizer's parameter, so gradients never flow back to the actual parameter being optimized.

## The Problem

This line is the culprit:

```python
with torch.no_grad():
    density_gain = torch.clamp(density_gain.detach().clone(), 0, 100)
```

\ue203When you call `.detach().clone()`, you create a completely new tensor that's disconnected from the computational graph.\ue204\ue202turn0search0 The optimizer still holds a reference to the *original* `density_gain` tensor, but you've replaced the variable with a new, detached tensor. When you later manually assign gradients with `density_gain.grad = torch.tensor(gain_acc)`, you're assigning gradients to this new tensor, not the one the optimizer is tracking.

## The Solution

You have several options to fix this:

### Option 1: Clamp with gradient support (recommended)
Simply remove the `torch.no_grad()` and `detach()` calls, and let `torch.clamp()` operate normally in the forward pass:

```python
# Remove the manual clamping block entirely
# Let clamp be part of the computational graph
dense_volume = make_dense_volume(input_tensor * torch.clamp(density_gain, 0, 100))
```

`torch.clamp()` is differentiable and will properly propagate gradients\ue202turn0search0.

### Option 2: In-place clamping (if you need it between iterations)
If you need to constrain the parameter values between optimization steps, do it *after* `optim.step()`:

```python
optim.step()

# Clamp in-place after the optimizer updates
with torch.no_grad():
    density_gain.clamp_(0, 100)  # Note: in-place operation with underscore
```

This way, you're modifying the actual parameter tensor the optimizer is tracking, not creating a new one.

### Option 3: Use optimizer parameter projection
For a cleaner approach, you could use a projection callback or a custom optimizer step:

```python
optim.step()

# Project parameters back to valid range
with torch.no_grad():
    for param in [density_gain]:
        param.data.clamp_(0, 100)
```

## Why Your Current Approach Fails

1. **Variable reassignment**: `density_gain = torch.clamp(...)` creates a new tensor and rebinds the variable name
2. **Optimizer disconnect**: The optimizer's internal parameter list still points to the *old* tensor
3. **Gradient assignment to wrong tensor**: Your manual gradient assignment `density_gain.grad = torch.tensor(gain_acc)` updates the new tensor, not the optimizer's parameter
4. **Zero gradients**: The optimizer sees zero gradients on its tracked parameter because nothing has updated it

The key insight is that \ue203in PyTorch, when you use `detach()`, it creates a tensor that doesn't require gradients and has no computational history\ue204\ue202turn0search0, and reassigning a variable doesn't update the optimizer's reference to the original parameter.


